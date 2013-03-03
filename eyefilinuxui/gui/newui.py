'''
Created on Mar 2, 2013

@author: Horacio G. de Oro
'''

import json
import logging
import pika
import sys

import PySide

from PySide import QtCore, QtGui
from pika.exceptions import AMQPConnectionError


# http://stackoverflow.com/questions/13302908/better-way-of-going-from-pil-to-pyside-qimage
sys.modules['PyQt4'] = PySide # HACK for ImageQt

import Image
import ImageQt

from eyefilinuxui.util import EVENT_QUEUE_NAME, get_exif_tags
from eyefilinuxui.gui.ui.mainwindow_ui import Ui_MainWindow


logger = logging.getLogger(__name__)


class RabbitMQEventReaderThread(QtCore.QThread):

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

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
            channel.start_consuming()
        except AMQPConnectionError:
            raise


#
# To build:
#
# $ pyside-uic eyefilinuxui/gui/ui/mainwindow.ui > eyefilinuxui/gui/ui/mainwindow_ui.py
#

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.scene = QtGui.QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.image = None
        self.imageQt = None
        self.pixMap = None
        self.image_rotate = 0

        self.resize(800, 600)
        self.splitter.setSizes([600, 180])

        # Create thread and connect
        self.rabbitmq_reader_thread = RabbitMQEventReaderThread()
        self.connect(self.rabbitmq_reader_thread,
            QtCore.SIGNAL("display_image(QString)"),
            self.display_image)
        self.connect(self.splitter,
            QtCore.SIGNAL("splitterMoved(int, int)"),
            self._do_resize)
        self.rabbitmq_reader_thread.start()

    def _do_resize(self):
        if self.image:
            w, h = self.image.size
            self.graphicsView.fitInView(QtCore.QRectF(0, 0, w, h), QtCore.Qt.KeepAspectRatio)
            self.scene.update()

    def resizeEvent(self, event):
        self._do_resize()

    def display_image(self, image_filename):
        self.image = Image.open(image_filename)
        self.scene.clear()
        self.tableWidgetExif.clear()
        self.tableWidgetExif.setColumnCount(1)
        self.tableWidgetExif.setHorizontalHeaderLabels(["Value"])
        self.image_rotate = 0
        self.graphicsView.resetTransform()
        self.graphicsView.resetMatrix()

        while self.tableWidgetExif.rowCount():
            self.tableWidgetExif.removeRow(0)

        exif_dict_to_show, other_dict = get_exif_tags(image_filename)
        exif_keys = sorted(exif_dict_to_show.keys())
        if exif_dict_to_show:
            for row_num in range(0, len(exif_dict_to_show)):
                valueItem = QtGui.QTableWidgetItem()
                valueItem.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
                valueItem.setFlags(valueItem.flags() ^ QtCore.Qt.ItemIsEditable)
                valueItem.setText(unicode(exif_dict_to_show[exif_keys[row_num]]))
                self.tableWidgetExif.insertRow(row_num)
                self.tableWidgetExif.setItem(row_num, 0, valueItem)
            self.tableWidgetExif.setVerticalHeaderLabels(exif_keys)
            self.tableWidgetExif.resizeColumnsToContents()

            #    In [21]: y = x['Image Orientation']
            #
            #    In [22]: EXIF.EXIF_TAGS[y.tag]
            #    Out[22]:
            #    ('Orientation',
            #     {1: 'Horizontal (normal)',
            #      2: 'Mirrored horizontal',
            #      3: 'Rotated 180',
            #      4: 'Mirrored vertical',
            #      5: 'Mirrored horizontal then rotated 90 CCW',
            #      6: 'Rotated 90 CW',
            #      7: 'Mirrored horizontal then rotated 90 CW',
            #      8: 'Rotated 90 CCW'})
            try:
                if 'Image Orientation' in other_dict:
                    image_orientation = other_dict['Image Orientation'].values[0]
                    if image_orientation == 3:
                        self.image_rotate = 180
                    elif image_orientation == 6:
                        self.image_rotate = 90
                    elif image_orientation == 8:
                        self.image_rotate = -90
            except:
                logger.exception("Couldn't get orientation from EXIF")

        self.statusBar.showMessage("Image: {0}".format(image_filename))
        self.imageQt = ImageQt.ImageQt(self.image)
        self.pixMap = QtGui.QPixmap.fromImage(self.imageQt, QtCore.Qt.ImageConversionFlag.AutoColor)
        self.scene.addPixmap(self.pixMap)
        self.graphicsView.rotate(self.image_rotate)
        self._do_resize()


def start_gui():
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    # window.display_image(sys.argv[1])
    # app.exec_()
    return app, window

if __name__ == '__main__':
    app, window = start_gui()
    sys.exit(app.exec_())
