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

from PySide import QtCore

from eyefilinuxui.util import _send_amqp_msg, \
    UDHCPD_QUEUE_NAME, HOSTAPD_QUEUE_NAME, create_child_management_event, \
    MSG_CHECK_CHILD


logger = logging.getLogger(__name__)


class RabbitMQKeepAliveThread(QtCore.QThread):

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self._run = True

    def run(self):
        origin = 'RabbitMQKeepAliveThread'
        logger.info("Starting thread...")
        while self._run:
            logger.debug("Sending keepalives...")
            _send_amqp_msg(create_child_management_event(origin, MSG_CHECK_CHILD),
                UDHCPD_QUEUE_NAME)
            _send_amqp_msg(create_child_management_event(origin, MSG_CHECK_CHILD),
                HOSTAPD_QUEUE_NAME)
            time.sleep(3)
