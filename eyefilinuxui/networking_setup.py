'''
Created on Mar 2, 2013

@author: Horacio G. de Oro
'''

import logging
import subprocess

logger = logging.getLogger(__name__)


def nm_interface_exists(interface):
    """Returns True if interface exists"""
    # $ nmcli -t -f DEVICE dev
    # wlan0
    # eth0
    output = subprocess.check_output(["nmcli", "-t", "-f", "DEVICE", "dev"])
    logger.debug("OUTPUT: %s", output)
    return interface in [l.strip() for l in output.strip().splitlines() if l.strip()]


def nm_check_disconnected(interface):
    """Returns True if interface is disconnected"""
    # $ nmcli -t -f DEVICE,STATE dev
    # wlan0:disconnected
    # eth0:connected
    output = subprocess.check_output(["nmcli", "-t", "-f", "DEVICE,STATE", "dev"])
    for line in [l.strip() for l in output.strip().splitlines() if l.strip()]:
        dev, state = line.split(':')
        if dev == interface:
            if state == 'disconnected':
                logger.info("GOOD! Device %s is disconnected.", interface)
                return True
            else:
                logger.warn("Device %s isn't disconnected - Device state: %s", interface, state)
                return False
    logger.warn("nmcli doesn't returned info for interface %s", interface)
    return False


def nm_try_disconnect(interface):
    return subprocess.call(["nmcli", "dev", "disconnect", "iface", interface])


def ifconfig(interface, ip):
    return subprocess.call(["kdesudo", "--", "ifconfig", interface, "{0}/24".format(ip)])


def iptables(interface, ip):
    # FIXME: put comments and check it to not repeat the setup of firewall every time the app starts
    return subprocess.call(["kdesudo", "--", "iptables", "-I", "INPUT", "-i", interface,
        "-p", "icmp", "-d", ip, "-j", "ACCEPT"])
    return subprocess.call(["kdesudo", "--", "iptables", "-I", "INPUT", "-i", interface,
        "-p", "tcp", "-d", ip, "--dport", "--", "59278", "-j", "ACCEPT"])
    return subprocess.call(["kdesudo", "--", "iptables", "-I", "INPUT", "-i", interface,
        "-p", "udp", "-d", ip, "--dport", "--", "67:68", "-j", "ACCEPT"])
