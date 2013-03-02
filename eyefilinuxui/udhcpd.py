'''
Created on Mar 2, 2013

@author: Horacio G. de Oro
'''

import logging
import os
import uuid

from multiprocessing import Pipe, Process

from eyefilinuxui.util import MSG_QUIT, MSG_START, \
    _recv_msg, MSG_GET_PID, _send_amqp_msg, generic_target,\
    generic_start_multiprocess

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

    # FIXME: create empty lease files
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


def _generate_test_config():
    """Call `start_udhcpd()` with some valid values to generate a config file for testing"""
    return udhcpd_gen_config('10.105.106.100', '10.105.106.199', 'wlan1',
        '10.105.106.2', '255.255.255.0', '10.105.106.2')


def _generic_start_multiprocess(start_args, action_map, _logger, queue_name, state):
    parent_conn, child_conn = Pipe()
    process = Process(target=generic_target, args=(
        child_conn,
        _logger,
        queue_name,
        start_args,
        action_map
    ))
    _logger.info("Launching child UDHCPD")
    process.start()

    process.info("Waiting for ACK")
    parent_conn.recv()
    process.info("ACK received...")

    state['running'] = True
    state['parent_conn'] = parent_conn
    state['process'] = process

    _send_amqp_msg({'action': MSG_START}, queue_name)


# FIXME: lock
def start_udhcpd(config_filename):
    start_args = ["sudo", "busybox", "udhcpd", "-f", config_filename]
    action_map = {}
    generic_start_multiprocess(start_args, action_map, logger, QUEUE_NAME, STATE)


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
