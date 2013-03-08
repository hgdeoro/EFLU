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
import os
import time
import unittest

from eyefilinuxui.gui.newui import start_gui
from eyefilinuxui.util import send_event, create_upload_event


class TestMain(unittest.TestCase):

    def test_main(self):
        logging.basicConfig(level=logging.DEBUG)
        base_dir = os.path.join(os.path.dirname(__file__), '../..')

        # First, check at least one test image exists
        filename = os.path.join(base_dir, 'test_image_0001.jpg')
        assert os.path.exists(filename), \
            "At least one test image should exists at the root of the project, " + \
            "with the format `test_image_0001.jpg`, `test_image_0002.jpg`, etc."

        app, window = start_gui()
        app.processEvents()
        logging.info("Waiting to start consuming messages...")
        while not window.rabbitmq_reader_thread.consuming:
            app.processEvents()
            time.sleep(0.1)
            app.processEvents()
        logging.info("Ok, we are consuming messages now...")

        for seq in xrange(1, 20):
            for _ in xrange(1, 20):
                app.processEvents()
                time.sleep(0.05)
            app.processEvents()
            filename = os.path.join(base_dir, 'test_image_{:04d}.jpg'.format(seq))
            if os.path.exists(filename):
                logging.info("Test image exists: '%s'. Will send event...", filename)
                send_event(create_upload_event('test', filename))
            else:
                break
        logging.info("Done!")
        app.exec_()
