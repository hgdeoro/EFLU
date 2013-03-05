'''
Created on Mar 2, 2013

@author: Horacio G. de Oro
'''

import logging
import os

from eyefilinuxui.util import generic_start_multiprocess, generic_mp_get_pid_of_ultimate_child, \
    generic_mp_stop, UDHCPD_QUEUE_NAME, generic_mp_check_subprocess

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


# FIXME: lock
def start_udhcpd(config_filename):
    start_args = ["sudo", "busybox", "udhcpd", "-f", config_filename]
    action_map = {}
    return generic_start_multiprocess(start_args, action_map, logger, UDHCPD_QUEUE_NAME, STATE)


# FIXME: lock
def stop_udhcpd():
    return generic_mp_stop(logger, UDHCPD_QUEUE_NAME, STATE)


# FIXME: lock
def get_udhcpd_pid():
    return generic_mp_get_pid_of_ultimate_child(logger, UDHCPD_QUEUE_NAME, STATE)


# FIXME: lock
def check_udhcpd_subprocess():
    generic_mp_check_subprocess(logger, STATE)
