'''
Created on Mar 2, 2013

@author: Horacio G. de Oro
'''

import logging
import os
import pprint
import subprocess

from multiprocessing import Pipe, Process

from eyefilinuxui.util import MSG_QUIT, MSG_START, _send_msg, MSG_GET_PID,\
    _recv_msg

logger = logging.getLogger(__name__)

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

    process = None

    while True:
        if conn.poll(1):
            # Got a message
            msg = conn.recv()
            logger.info("Message received: %s", pprint.pformat(msg))
            if msg['action'] == MSG_QUIT:
                break
            if msg['action'] == MSG_START:
                with open('/tmp/.eyefi-hostapd.conf', 'r') as config_file:
                    for line in config_file.readlines():
                        logger.debug(".eyefi-hostapd.conf >> %s", line.strip())

                args = ["sudo", "hostapd", msg['config_file']]
                logger.info("Will Popen with args: %s", pprint.pformat(args))
                process = subprocess.Popen(args, close_fds=True, cwd='/')
                logger.info("Popen returded process %s", process)
            if msg['action'] == MSG_GET_PID:
                response = {}
                if '_uuid' in msg:
                    response['_uuid'] = msg['_uuid']
                response['pid'] = None
                if process:
                    response['pid'] = process.pid

                conn.send(response)


def start_hostapd():
    # Detect errors earlier...
    config_filename = hostapd_gen_config('wlan1', 'som-network-name', ('12:12:12:12:12:12',), 'wifipass')

    hostapd_parent_conn, hostapd_child_conn = Pipe()
    hostapd_process = Process(target=_hostapd_target, args=(hostapd_child_conn,))
    logging.info("Launching child HOSTAPD")
    hostapd_process.start()

    STATE['running'] = True
    STATE['parent_conn'] = hostapd_parent_conn
    STATE['process'] = hostapd_process

    _send_msg(STATE, {'action': MSG_START,
        'config_file': config_filename})


def stop_hostapd():
    logger.info("Stopping hostapd...")
    _send_msg(STATE, {'action': MSG_QUIT})
    STATE['running'] = False
    logger.info("Waiting for process.join() on pid %s...", STATE['process'].pid)
    STATE['process'].join()
    logger.info("Process exit status: %s", STATE['process'].exitcode)


# FIXME: lock
def get_hostapd_pid():
    """Returns the PID, or None if not running"""
    msg_uuid = _send_msg(STATE, {'action': MSG_GET_PID})
    msg = _recv_msg(STATE, msg_uuid=msg_uuid)
    return msg['pid']
