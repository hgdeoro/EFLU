'''
Created on Mar 2, 2013

@author: Horacio G. de Oro
'''

import logging
import time
import unittest
from eyefilinuxui.eyefiserver2_adaptor import start_eyefiserver2,\
    _generate_test_config, stop_eyefiserver2


class TestLaunchEyeFiServer2(unittest.TestCase):

    def test_launch(self):
        logging.basicConfig(level=logging.DEBUG)
        start_eyefiserver2(_generate_test_config())
        count = range(0, 5)
        while count and count.pop():
            time.sleep(1)
        stop_eyefiserver2()
