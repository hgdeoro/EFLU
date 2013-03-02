'''
Created on Mar 2, 2013

@author: Horacio G. de Oro
'''

import logging
import time
import unittest

from eyefilinuxui.hostapd import start_hostapd, get_hostapd_pid, stop_hostapd, _generate_test_config


class LaunchTest(unittest.TestCase):

    def test_launch(self):
        logging.basicConfig(level=logging.DEBUG)
        start_hostapd(_generate_test_config())
        pid = get_hostapd_pid()
        count = range(0, 5)
        while pid and count:
            print "PID >>>", pid
            pid = get_hostapd_pid()
            count.pop()
            time.sleep(1)

        stop_hostapd()
