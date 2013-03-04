'''
Created on Mar 3, 2013

@author: Horacio G. de Oro
'''

import json
import logging
import pika

from PySide import QtCore
from pika.exceptions import AMQPConnectionError

from eyefilinuxui.util import EVENT_QUEUE_NAME


logger = logging.getLogger(__name__)


class RabbitMQEventReaderThread(QtCore.QThread):

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.consuming = False

    def callback(self, ch, method, properties, msg):
        logger.info("MSG recibido: %s", msg)
        msg = json.loads(msg)
        if msg['origin'] == 'eyefiserver' and msg['type'] == 'upload' and msg['extra']:
            if 'filename' in msg['extra']:
                self.emit(
                    QtCore.SIGNAL("display_image(QString)"),
                    msg['extra']['filename'],
                )

        #    send_event('eyefiserver', 'upload', {
        #        'filename': imagePath,
        #    })
        #    msg = {
        #        'origin': origin,
        #        'type': event_type,
        #        'extra': extra,
        #    }

    def run(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.exchange_declare(exchange=EVENT_QUEUE_NAME, type='fanout')
        result = channel.queue_declare(exclusive=True)
        _queue_name = result.method.queue
        channel.queue_bind(exchange=EVENT_QUEUE_NAME, queue=_queue_name)

        channel.basic_consume(self.callback, queue=_queue_name, no_ack=True)
        try:
            self.consuming = True
            channel.start_consuming()
        except AMQPConnectionError:
            raise
