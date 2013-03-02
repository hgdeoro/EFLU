'''
Created on Mar 2, 2013

@author: Horacio G. de Oro
'''

import logging
import os

from eyefilinuxui.util import generic_start_multiprocess, \
    generic_mp_get_pid, generic_mp_stop

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


def _generate_test_config():
    """Call `hostapd_gen_config()` with some valid values to generate a config file for testing"""
    return hostapd_gen_config('wlan1', 'som-network-name', ('12:12:12:12:12:12',), 'wifipass')


# FIXME: lock
def start_hostapd(config_filename):
    start_args = ["sudo", "hostapd", config_filename]
    action_map = {}
    return generic_start_multiprocess(start_args, action_map, logger, QUEUE_NAME, STATE)


# FIXME: lock
def stop_hostapd():
    return generic_mp_stop(logger, QUEUE_NAME, STATE)


# FIXME: lock
def get_hostapd_pid():
    """Returns the PID, or None if not running"""
    return generic_mp_get_pid(logger, QUEUE_NAME, STATE)
