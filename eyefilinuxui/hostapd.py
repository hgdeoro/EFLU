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

from eyefilinuxui.util import MSG_QUIT, MSG_START, MSG_GET_PID,\
    _recv_msg, _send_amqp_msg

logger = logging.getLogger(__name__)

QUEUE_NAME = 'eflu.hostapd'

CONFIG_FILE = '/tmp/.eyefi-hostapd.conf'
ACCEPT_MAC_FILE = '/tmp/.eyefi-hostapd.accept'

STATE = {
    'running': False,
    'parent_conn': None,
    'process': None,
}


def hostapd_gen_config(interface, ssid, accepted_mac_list, wpa_passphrase):
    """Creates the configuration file"""
    template_filename = os.path.join(os.path.dirname(__file__), 'templates/hostapd.conf.template')
    with open(template_filename, 'r') as t:
        template = t.read()

    with open(ACCEPT_MAC_FILE, 'w') as accepted_mac_config_file:
        for mac in accepted_mac_list:
            accepted_mac_config_file.write(mac)
            accepted_mac_config_file.write('\n')

    # FIXME: sets permissions!
    config_contents = template % {
        'interface': interface,
        'ssid': ssid,
        'wpa_passphrase': wpa_passphrase,
        'accept_mac_file': ACCEPT_MAC_FILE,
    }

    with open(CONFIG_FILE, 'w') as config_file:
        config_file.write(config_contents)
    return CONFIG_FILE


def _hostapd_target(conn):
    logger = logging.getLogger('hostapd-child')
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
            while process:
                process.pop()
            connection.close()
            return

        if msg['action'] == MSG_START:
            if process:
                # FIXME: raise error? stop old process? warn and continue?
                logging.warn("A process exists: %s. It will be overriden", process[0])
                while process:
                    process.pop()

            with open('/tmp/.eyefi-hostapd.conf', 'r') as config_file:
                for line in config_file.readlines():
                    logger.debug(".eyefi-hostapd.conf >> %s", line.strip())
    
            args = ["sudo", "hostapd", msg['config_file']]
            logger.info("Will Popen with args: %s", pprint.pformat(args))
            process.append(subprocess.Popen(args, close_fds=True, cwd='/'))
            logger.info("Popen returded process %s", process)
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
                    while process:
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


def _generate_test_config():
    """Call `hostapd_gen_config()` with some valid values to generate a config file for testing"""
    return hostapd_gen_config('wlan1', 'som-network-name', ('12:12:12:12:12:12',), 'wifipass')


# FIXME: lock
def start_hostapd(config_filename):
    hostapd_parent_conn, hostapd_child_conn = Pipe()
    hostapd_process = Process(target=_hostapd_target, args=(hostapd_child_conn,))
    logging.info("Launching child HOSTAPD")
    hostapd_process.start()

    logging.info("Waiting for ACK")
    hostapd_parent_conn.recv()
    logging.info("ACK received...")

    STATE['running'] = True
    STATE['parent_conn'] = hostapd_parent_conn
    STATE['process'] = hostapd_process

    _send_amqp_msg({'action': MSG_START, 'config_file': config_filename}, QUEUE_NAME)


# FIXME: lock
def stop_hostapd():
    logger.info("Stopping hostapd...")
    _send_amqp_msg({'action': MSG_QUIT}, QUEUE_NAME)
    STATE['running'] = False
    logger.info("Waiting for process.join() on pid %s...", STATE['process'].pid)
    STATE['process'].join()
    logger.info("Process exit status: %s", STATE['process'].exitcode)


# FIXME: lock
def get_hostapd_pid():
    """Returns the PID, or None if not running"""
    msg_uuid = str(uuid.uuid4())
    _send_amqp_msg({'_uuid': msg_uuid, 'action': MSG_GET_PID}, QUEUE_NAME)

    msg = _recv_msg(STATE, msg_uuid=msg_uuid)
    return msg['pid']
