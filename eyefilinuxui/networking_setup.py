'''
Created on Mar 2, 2013

@author: Horacio G. de Oro
'''

import logging
import subprocess
from eyefilinuxui.util import kdesudo

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
    return kdesudo(["ifconfig", interface, "{0}/24".format(ip)])


def iptables(interface, ip):
    # FIXME: put comments and check it to not repeat the setup of firewall every time the app starts
    iptables_rules = subprocess.check_output(["kdesudo", "--", "iptables", "-n", "-v", "-L", "INPUT"])
    logger.debug("iptables_rules: %s", iptables_rules)

    if iptables_rules.find("/* EyeFiServerUi/1 */") == -1:
        kdesudo(["iptables", "-I", "INPUT", "-i", interface,
            "-p", "icmp", "-d", ip, "-m", "comment", "--comment", "EyeFiServerUi/1", "-j", "ACCEPT"])
    if iptables_rules.find("/* EyeFiServerUi/2 */") == -1:
        kdesudo(["iptables", "-I", "INPUT", "-i", interface,
            "-p", "tcp", "-d", ip, "-m", "comment", "--comment", "EyeFiServerUi/2",
            "--dport", "59278", "-j", "ACCEPT"])
    if iptables_rules.find("/* EyeFiServerUi/3 */") == -1:
        kdesudo(["iptables", "-I", "INPUT", "-i", interface,
            "-p", "udp", "-d", ip, "-m", "comment", "--comment", "EyeFiServerUi/3",
            "--dport", "67:68", "-j", "ACCEPT"])
