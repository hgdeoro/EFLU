'''
Created on Mar 2, 2013

@author: Horacio G. de Oro
'''

import logging

from eyefilinuxui.hostapd import start_hostapd, stop_hostapd
from eyefilinuxui.udhcpd import start_udhcpd, stop_udhcpd

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)

    logger.info("--- STARTING ---")
    start_hostapd()
    start_udhcpd()

    logger.info("--- FINISHING ---")
    stop_hostapd()
    stop_udhcpd()

if __name__ == '__main__':
    main()
