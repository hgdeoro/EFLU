'''
Created on Mar 2, 2013

@author: Horacio G. de Oro
'''

import logging

from multiprocessing import Process, Pipe

from eyefilinuxui.util import MSG_START, MSG_QUIT
from eyefilinuxui.hostapd import hostapd, hostapd_gen_config

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)
    hostapd_parent_conn, hostapd_child_conn = Pipe()
    hostapd_process = Process(target=hostapd, args=(hostapd_child_conn,))
    logging.info("Launching child HOSTAPD")
    hostapd_process.start()

    # Generamos configuracion
    with open('/tmp/.eyefi-hostapd.conf', 'w') as f:
        f.write("Contenido de ejemplo")

    hostapd_gen_config('wlan1', 'som-network-name', ('12:12:12:12:12:12',), 'wifipass')

    hostapd_parent_conn.send({'action': MSG_START,
        'config_file': '/tmp/.eyefi-hostapd.conf'})

    hostapd_parent_conn.send({'action': MSG_QUIT, })

if __name__ == '__main__':
    main()
