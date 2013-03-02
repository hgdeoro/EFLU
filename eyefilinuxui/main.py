'''
Created on Mar 2, 2013

@author: Horacio G. de Oro
'''

import logging

from multiprocessing import Process, Pipe

from eyefilinuxui.util import MSG_START, MSG_QUIT
from eyefilinuxui.hostapd import hostapd, hostapd_gen_config
from eyefilinuxui.dhcpd import udhcpd_gen_config, udhcpd

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)

    #===========================================================================
    # hostapd
    #===========================================================================
    hostapd_parent_conn, hostapd_child_conn = Pipe()
    hostapd_process = Process(target=hostapd, args=(hostapd_child_conn,))
    logging.info("Launching child HOSTAPD")
    hostapd_process.start()

    config_filename = hostapd_gen_config('wlan1', 'som-network-name', ('12:12:12:12:12:12',), 'wifipass')

    hostapd_parent_conn.send({'action': MSG_START,
        'config_file': config_filename})

    hostapd_parent_conn.send({'action': MSG_QUIT, })

    #===========================================================================
    # udhcpd
    #===========================================================================
    udhcpd_parent_conn, udhcpd_child_conn = Pipe()
    udhcpd_process = Process(target=udhcpd, args=(udhcpd_child_conn,))
    logging.info("Launching child UDHCPD")
    udhcpd_process.start()

    config_filename = udhcpd_gen_config('10.105.106.100', '10.105.106.199', 'wlan1',
        '10.105.106.2', '255.255.255.0', '10.105.106.2')

    udhcpd_parent_conn.send({'action': MSG_START,
        'config_file': config_filename})

    udhcpd_parent_conn.send({'action': MSG_QUIT, })

if __name__ == '__main__':
    main()
