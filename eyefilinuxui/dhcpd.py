'''
Created on Mar 2, 2013

@author: Horacio G. de Oro
'''

import logging
import os
import pprint

from eyefilinuxui.util import MSG_QUIT, MSG_START

logger = logging.getLogger(__name__)

CONFIG_FILE = '/tmp/.eyefi-udhcpd.conf'
PID_FILE = '/tmp/.eyefi-udhcpd.pid'
LEASE_FILE = '/tmp/.eyefi-udhcpd-leases'


def udhcpd_gen_config(start, end, interface, opt_dns, opt_subnet, opt_router, pidfile=PID_FILE, lease_file=LEASE_FILE):
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


def udhcpd(conn):
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
