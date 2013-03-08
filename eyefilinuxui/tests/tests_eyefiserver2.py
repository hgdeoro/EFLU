# coding=utf-8

#----------------------------------------------------------------------
# Copyright (c) 2013 Horacio G. de Oro <hgdeoro@gmail.com>
#----------------------------------------------------------------------
#    This file is part of EFLU.
#
#    EFLU is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    EFLU is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with EFLU.  If not, see <http://www.gnu.org/licenses/>.
#----------------------------------------------------------------------

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
