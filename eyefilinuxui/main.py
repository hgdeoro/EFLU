'''
Created on Mar 2, 2013

@author: Horacio G. de Oro
'''

import logging
import pprint

from multiprocessing import Process, Pipe
import os

logger = logging.getLogger(__name__)

MSG_START = 'start'
MSG_QUIT = 'quit'


def hostapd_gen_config(interface, ssid, accepted_mac_list, wpa_passphrase):
    template_filename = os.path.join(os.path.dirname(__file__), 'templates/hostapd.conf.template')
    with open(template_filename, 'r') as t:
        template = t.read()

    with open('/tmp/.eyefi-hostapd.accept', 'w') as accepted_mac_config_file:
        for mac in accepted_mac_list:
            accepted_mac_config_file.write(mac)
            accepted_mac_config_file.write('\n')

    # FIXME: sets permissions!
    config_contents = template % {
        'interface': interface,
        'ssid': ssid,
        'wpa_passphrase': wpa_passphrase,
        'accept_mac_file': '/tmp/.eyefi-hostapd.accept',
    }

    with open('/tmp/.eyefi-hostapd.conf', 'w') as config_file:
        config_file.write(config_contents)


def hostapd(conn):
    logger = logging.getLogger('hostapd')
    logger.info("Waiting for message...")
    while True:
        msg = conn.recv()
        logger.info("Message received")
        logger.debug("Msg: %s", pprint.pformat(msg))
        if msg['action'] == MSG_QUIT:
            break
        if msg['action'] == MSG_START:
            with open('/tmp/.eyefi-hostapd.conf', 'r') as config_file:
                for line in config_file.readlines():
                    logging.debug(".eyefi-hostapd.conf >> %s", line.strip())


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
