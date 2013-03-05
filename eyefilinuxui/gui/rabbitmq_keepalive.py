'''
Created on Mar 4, 2013

@author: Horacio G. de Oro
'''

import logging

from PySide import QtCore

from eyefilinuxui.util import _send_amqp_msg, \
    UDHCPD_QUEUE_NAME, HOSTAPD_QUEUE_NAME, create_child_management_event, \
    MSG_CHECK_CHILD
import time


logger = logging.getLogger(__name__)


class RabbitMQKeepAliveThread(QtCore.QThread):

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.run = True

    def run(self):
        origin = 'RabbitMQKeepAliveThread'
        while self.run:
            logger.debug("Sending keepalives...")
            _send_amqp_msg(create_child_management_event(origin, MSG_CHECK_CHILD),
                UDHCPD_QUEUE_NAME)
            _send_amqp_msg(create_child_management_event(origin, MSG_CHECK_CHILD),
                HOSTAPD_QUEUE_NAME)
            time.sleep(3)
