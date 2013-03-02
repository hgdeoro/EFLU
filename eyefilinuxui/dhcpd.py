'''
Created on Mar 2, 2013

@author: Horacio G. de Oro
'''

import logging
import os
import pprint

from multiprocessing import Pipe, Process

from eyefilinuxui.util import MSG_QUIT, MSG_START, _send_msg

logger = logging.getLogger(__name__)

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
    while True:
        msg = conn.recv()
        logger.info("Message received")
        logger.debug("Msg: %s", pprint.pformat(msg))
        if msg['action'] == MSG_QUIT:
            break
        if msg['action'] == MSG_START:
            with open(CONFIG_FILE, 'r') as config_file:
                for line in config_file.readlines():
                    logger.debug("CONFIG >> %s", line.strip())


def start_udhcpd():
    udhcpd_parent_conn, udhcpd_child_conn = Pipe()
    udhcpd_process = Process(target=_udhcpd_target, args=(udhcpd_child_conn,))
    logging.info("Launching child UDHCPD")
    udhcpd_process.start()

    STATE['running'] = True
    STATE['parent_conn'] = udhcpd_parent_conn
    STATE['process'] = udhcpd_process

    config_filename = udhcpd_gen_config('10.105.106.100', '10.105.106.199', 'wlan1',
        '10.105.106.2', '255.255.255.0', '10.105.106.2')

    _send_msg(STATE, {'action': MSG_START,
        'config_file': config_filename})


def stop_udhcpd():
    logger.info("Stopping UDHCPD...")
    _send_msg(STATE, {'action': MSG_QUIT})
    STATE['running'] = False
    logger.info("Waiting for process.join() on pid %s...", STATE['process'].pid)
    STATE['process'].join()
    logger.info("Process exit status: %s", STATE['process'].exitcode)
