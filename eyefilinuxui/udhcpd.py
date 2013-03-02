'''
Created on Mar 2, 2013

@author: Horacio G. de Oro
'''

import json
import logging
import os
import pika
import pprint
import subprocess
import uuid

from multiprocessing import Pipe, Process
from pika.exceptions import AMQPConnectionError

from eyefilinuxui.util import MSG_QUIT, MSG_START, \
    _recv_msg, MSG_GET_PID, _send_amqp_msg

logger = logging.getLogger(__name__)

QUEUE_NAME = 'eflu.udhcpd'

CONFIG_FILE = '/tmp/.eyefi-udhcpd.conf'
PID_FILE = '/tmp/.eyefi-udhcpd.pid'
LEASE_FILE = '/tmp/.eyefi-udhcpd-leases'

STATE = {
    'running': False,
    'parent_conn': None,
    'process': None,
}


def udhcpd_gen_config(start, end, interface, opt_dns, opt_subnet, opt_router, pidfile=PID_FILE, lease_file=LEASE_FILE):
    """Creates the configuration file"""
    template_filename = os.path.join(os.path.dirname(__file__), 'templates/busybox-udhcpd.conf.template')
    with open(template_filename, 'r') as t:
        template = t.read()

    # FIXME: sets permissions!
    config_contents = template % {
        'start': start,
        'end': end,
        'interface': interface,
        'pidfile': pidfile,
        'lease_file': lease_file,
        'opt_dns': opt_dns,
        'opt_subnet': opt_subnet,
        'opt_router': opt_router,
    }

    with open(CONFIG_FILE, 'w') as config_file:
        config_file.write(config_contents)
    return CONFIG_FILE


def _udhcpd_target(conn):
    logger = logging.getLogger('udhcpd-child')
    logger.info("Waiting for message...")

    process = []
    closing_connection = [False]

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange=QUEUE_NAME, type='fanout')
    result = channel.queue_declare(exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=QUEUE_NAME, queue=queue_name)

    def callback(ch, method, properties, msg):
        msg = json.loads(msg)
        logger.info("Message received: %s", pprint.pformat(msg))

        if msg['action'] == MSG_QUIT:
            closing_connection[0] = True
            if process:
                logging.warn("A process exists: %s", process[0])
            # FIXME: stop process if exists?
            process.pop()
            connection.close()
            return

        if msg['action'] == MSG_START:
            if process:
                # FIXME: raise error? stop old process? warn and continue?
                logging.warn("A process exists: %s. It will be overriden", process[0])
                process.pop()
            with open(CONFIG_FILE, 'r') as config_file:
                for line in config_file.readlines():
                    logger.debug("CONFIG >> %s", line.strip())
            args = ["sudo", "busybox", "udhcpd", "-f", msg['config_file']]
            logger.info("Will Popen with args: %s", pprint.pformat(args))
            process.append(subprocess.Popen(args, close_fds=True, cwd='/'))
            logger.info("Popen returded process %s", process[0])
            return

        if msg['action'] == MSG_GET_PID:
            response = {}
            if '_uuid' in msg:
                response['_uuid'] = msg['_uuid']
            response['pid'] = None
            if process[0]:
                response['pid'] = process[0].pid

            # data es sent over 'connection' (Pipe)
            conn.send(response)
            return

        if msg['action'] == "CHECK_CHILD":
            if process:
                # ret_code = process.wait()
                process[0].poll()
                if process[0].returncode is not None:
                    logger.info("Cleaning up finished Popen process. Exit status: %s", process[0].returncode)
                    if process[0].returncode != 0:
                        logger.warn("Exit status != 0")
                    process[0].wait()
                    process.pop()
                else:
                    logger.debug("Popen process %s is running", process[0])
            return

        logger.error("UNKNOWN MESSAGE: %s", pprint.pformat(msg))

    channel.basic_consume(callback, queue=queue_name, no_ack=True)
    conn.send("ACK")
    try:
        channel.start_consuming()
    except AMQPConnectionError:
        if closing_connection[0]:
            logger.info("Ignoring AMQPConnectionError")
        else:
            raise


# FIXME: lock
def start_udhcpd():
    # Detect errors earlier...
    config_filename = udhcpd_gen_config('10.105.106.100', '10.105.106.199', 'wlan1',
        '10.105.106.2', '255.255.255.0', '10.105.106.2')

    udhcpd_parent_conn, udhcpd_child_conn = Pipe()
    udhcpd_process = Process(target=_udhcpd_target, args=(udhcpd_child_conn,))
    logging.info("Launching child UDHCPD")
    udhcpd_process.start()

    logging.info("Waiting for ACK")
    udhcpd_parent_conn.recv()
    logging.info("ACK received...")

    STATE['running'] = True
    STATE['parent_conn'] = udhcpd_parent_conn
    STATE['process'] = udhcpd_process

    _send_amqp_msg({'action': MSG_START, 'config_file': config_filename}, QUEUE_NAME)


# FIXME: lock
def stop_udhcpd():
    logger.info("Stopping UDHCPD...")
    _send_amqp_msg({'action': MSG_QUIT}, QUEUE_NAME)
    STATE['running'] = False
    logger.info("Waiting for process.join() on pid %s...", STATE['process'].pid)
    STATE['process'].join()
    logger.info("Process exit status: %s", STATE['process'].exitcode)


# FIXME: lock
def get_udhcpd_pid():
    """Returns the PID, or None if not running"""
    msg_uuid = str(uuid.uuid4())
    _send_amqp_msg({'_uuid': msg_uuid, 'action': MSG_GET_PID}, QUEUE_NAME)

    msg = _recv_msg(STATE, msg_uuid=msg_uuid)
    return msg['pid']
