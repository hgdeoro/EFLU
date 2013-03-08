'''
Created on Mar 2, 2013

@author: Horacio G. de Oro
'''

import argparse
import logging
import socket
import sys
import time

from eyefilinuxui.hostapd import start_hostapd, stop_hostapd, hostapd_gen_config
from eyefilinuxui.udhcpd import start_udhcpd, stop_udhcpd, udhcpd_gen_config
from eyefilinuxui.networking_setup import nm_check_disconnected, \
    nm_try_disconnect, ifconfig, nm_interface_exists, iptables
from eyefilinuxui.eyefiserver2_adaptor import eyefiserver2_gen_config, \
    start_eyefiserver2, stop_eyefiserver2
from eyefilinuxui.gui.newui import start_gui
from eyefilinuxui.util import _check_amqp_connection, kdesudo
import subprocess

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='EyFi Linux Ui')
    parser.add_argument('--interface', help='wifi interface', default='wlan1', required=True)
    # parser.add_argument('--ip', help='ip to use on the wifi interface', default='10.105.106.2')
    parser.add_argument('--wifi_ssid', help='ssid to use for the wifi network', required=True)
    parser.add_argument('--wifi_passphrase', help='connection password of the wifi network', required=True)
    parser.add_argument('--mac_whitelist', help='MAC addresses to allow, separated by comas', default='')
    parser.add_argument('--eyefi_mac', help='MAC address of EyeFi card', required=True)
    parser.add_argument('--eyefi_upload_key', help='EyeFi secret (from Settings.xml)', required=True)
    parser.add_argument('--upload_dir', help='Directory to upload images', required=True)
    parser.add_argument('--debug', help='Set logging to debug level',
        action='store_true', default=False)

    args = parser.parse_args()

    # FIXME: validate arguments (ej: format of IP, MAC, upload dir perms, etc)

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('pika').setLevel(logging.INFO)
    else:
        logging.basicConfig(level=logging.INFO)

    if not nm_interface_exists(args.interface):
        parser.error("The interface {0} does not exists".format(args.interface))

    ip = "10.105.106.2"

    mac_whitelist = [m.strip() for m in args.mac_whitelist.strip().split(',') if m.strip()]
    if args.eyefi_mac not in mac_whitelist:
        mac_whitelist.append(args.eyefi_mac)
    for mac in mac_whitelist:
        if len(mac.split(':')) != 6 or list(set([len(x) for x in mac.split(':')])) != [2]:
            parser.error("Invalid MAC: '{0}' - Use `xx:xx:xx:xx:xx:xx` format".format(mac))

    for command in ("kdesudo", "hostapd", "busybox", "rabbitmqctl", "nmcli"):
        ret = subprocess.call(["which", command])
        if ret != 0:
            print "ERROR: you don't have '{0}' installed or in the path...".format(command)
            sys.exit(1)

    busybox_list = subprocess.check_output(["busybox", "--list"])
    if busybox_list.find("udhcpd") == -1:
        print "ERROR: you don't have the 'udhcpd' applet of BusyBox..."
        sys.exit(1)

    try:
        _check_amqp_connection()
    except socket.error:
        # TODO: maybe we could start the gui even if rabbitmq isn't working
        logger.warn("Couldn't connect to RabbitMQ... Will try to connect...")
        kdesudo(["sudo", "service", "rabbitmq-server", "start"])

        try:
            _check_amqp_connection()
        except socket.error:
            print "ERROR: couldn't connect to RabbitMQ"
            sys.exit(1)

    #===========================================================================
    # Start the UI
    #===========================================================================

    qt_app, _ = start_gui()
    qt_app.processEvents()

    # FIXME: here we should call app.exec_() and do the initialization in a thread

    #===========================================================================
    # Configure the interface
    #===========================================================================

    # Check if interface is in use using Network Manager cli
    ok = nm_check_disconnected(args.interface)
    if not ok:
        nm_try_disconnect(args.interface)
        qt_app.processEvents()

    ifconfig(args.interface, ip)
    qt_app.processEvents()

    iptables(args.interface, ip)
    qt_app.processEvents()

    #===========================================================================
    # HostAP
    #===========================================================================
    hostapd_config_filename = hostapd_gen_config(
        args.interface,
        args.wifi_ssid,
        mac_whitelist,
        args.wifi_passphrase
    )

    start_hostapd(hostapd_config_filename)
    qt_app.processEvents()

    #===========================================================================
    # uDHCPd
    #===========================================================================

    start = ".".join(ip.split(".")[0:3] + ["100"])
    end = ".".join(ip.split(".")[0:3] + ["199"])
    # start, end, interface, opt_dns, opt_subnet, opt_router, pidfile=PID_FILE, lease_file=LEASE_FILE
    udhcpd_config_filename = udhcpd_gen_config(
        start,
        end,
        args.interface,
        ip,
        "255.255.255.0",
        ip,
    )
    start_udhcpd(udhcpd_config_filename)
    qt_app.processEvents()

    #===========================================================================
    # EyeFiServer2
    #===========================================================================

    eyefiserver2_config = eyefiserver2_gen_config("".join(args.eyefi_mac.split(":")),
        args.eyefi_upload_key, args.upload_dir)

    start_eyefiserver2(eyefiserver2_config)
    qt_app.processEvents()

    try:
        qt_app.exec_()
        logging.warn("")
        logging.warn("")
        logging.warn("")
        logging.warn(" THE APP WILL CONTINUE RUNNING UNTIL YOU PRESS Ctrl+C")
        logging.warn("")
        logging.warn("")
        logging.warn("")
        while True:
            time.sleep(1)
        # Here we force the user to press Ctrl+C
        # FIXME: make subprocess exit even without pressing Ctrl+C
        # (don't know why doens't work without Ctrl+C)
    except KeyboardInterrupt:
        stop_hostapd()
        stop_udhcpd()
        stop_eyefiserver2()
        qt_app.quit()


if __name__ == '__main__':
    main()
