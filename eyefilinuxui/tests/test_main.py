'''
Created on Mar 2, 2013

@author: Horacio G. de Oro
'''

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
