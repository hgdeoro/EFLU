'''
Created on Mar 2, 2013

@author: Horacio G. de Oro
'''

import unittest
import logging

from eyefilinuxui.udhcpd import start_udhcpd, stop_udhcpd, get_udhcpd_pid
import time


class LaunchTest(unittest.TestCase):

    def test_launch(self):
        logging.basicConfig(level=logging.DEBUG)
        start_udhcpd()
        pid = get_udhcpd_pid()
        count = range(0, 5)
        while pid and count:
            print "PID >>>", pid
            pid = get_udhcpd_pid()
            count.pop()
            time.sleep(1)

        stop_udhcpd()
