'''
Created on Mar 2, 2013

@author: Horacio G. de Oro
'''

import logging
import time

from eyefilinuxui.hostapd import start_hostapd, stop_hostapd, hostapd_gen_config
from eyefilinuxui.udhcpd import start_udhcpd, stop_udhcpd, udhcpd_gen_config
import argparse
from eyefilinuxui.networking_setup import nm_check_disconnected,\
    nm_try_disconnect, ifconfig, nm_interface_exists

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='EyFi Linux Ui')

    parser.add_argument('--interface', help='wifi interface', default='wlan1', required=True)
    # parser.add_argument('--ip', help='ip to use on the wifi interface', default='10.105.106.2')
    parser.add_argument('--wifi_ssid', help='ssid to use for the wifi network', required=True)
    parser.add_argument('--wifi_passphrase', help='connection password of the wifi network', required=True)
    parser.add_argument('--mac_whitelist', help='MAC addresses to allow, separated by comas', default='',
        required=True)
    parser.add_argument('--eyefi_upload_key', help='EyeFi secret (from Settings.xml)', required=True)

    args = parser.parse_args()

    if not nm_interface_exists(args.interface):
        parser.error("The interface {0} does not exists".format(args.interface))

    ip = "10.105.106.2"

    #===========================================================================
    # Configure the interface
    #===========================================================================

    # Check if interface is in use using Network Manager cli
    ok = nm_check_disconnected(args.interface)
    if not ok:
        nm_try_disconnect(args.interface)

    # FIXME: setup firewall
    #    sudo iptables -I INPUT -i $IFACE -p icmp -j ACCEPT
    #    sudo iptables -I INPUT -i $IFACE -p tcp --dport 59278 -d $IP -j ACCEPT
    #    sudo iptables -I INPUT -i $IFACE -p udp --dport 67:68 -j ACCEPT
    #    sudo iptables -I FORWARD -i $IFACE -j REJECT
    #    sudo iptables -I FORWARD -o $IFACE -j REJECT

    ifconfig(args.interface, ip)

    #===========================================================================
    # HostAP
    #===========================================================================
    macs = [m.strip() for m in args.mac_whitelist.strip().split(',')]
    hostapd_config_filename = hostapd_gen_config(
        args.interface,
        args.wifi_ssid,
        macs,
        args.wifi_passphrase
    )

    start_hostapd(hostapd_config_filename)

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

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_hostapd()
        stop_udhcpd()

if __name__ == '__main__':
    main()
