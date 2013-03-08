# coding=utf-8

#----------------------------------------------------------------------
# Copyright (c) 2013 Horacio G. de Oro <hgdeoro@gmail.com>
#----------------------------------------------------------------------
#    This file is part of EFLU.
#
#    EFLU is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    EFLU is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with EFLU.  If not, see <http://www.gnu.org/licenses/>.
#----------------------------------------------------------------------

import logging
import os

from eyefilinuxui.util import generic_start_multiprocess, \
    generic_mp_get_pid_of_ultimate_child, generic_mp_stop, HOSTAPD_QUEUE_NAME, \
    generic_mp_check_subprocess

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


def _generate_test_config():
    """Call `hostapd_gen_config()` with some valid values to generate a config file for testing"""
    return hostapd_gen_config('wlan1', 'som-network-name', ('12:12:12:12:12:12',), 'wifipass')


# FIXME: lock
def start_hostapd(config_filename):
    start_args = ["kdesudo", "--", "hostapd", config_filename]
    action_map = {}
    return generic_start_multiprocess(start_args, action_map, logger, HOSTAPD_QUEUE_NAME, STATE)


# FIXME: lock
def stop_hostapd():
    return generic_mp_stop(logger, HOSTAPD_QUEUE_NAME, STATE)


# FIXME: lock
def get_hostapd_pid():
    """Returns the PID, or None if not running"""
    return generic_mp_get_pid_of_ultimate_child(logger, HOSTAPD_QUEUE_NAME, STATE)


# FIXME: lock
def check_hostapd_subprocess():
    generic_mp_check_subprocess(logger, STATE)
