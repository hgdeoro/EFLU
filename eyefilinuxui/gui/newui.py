'''
Created on Mar 2, 2013

@author: Horacio G. de Oro
'''

import logging
import sys

import PySide

from PySide import QtCore, QtGui
from eyefilinuxui.gui.rabbitmq_thread import RabbitMQEventReaderThread

# http://stackoverflow.com/questions/13302908/better-way-of-going-from-pil-to-pyside-qimage
sys.modules['PyQt4'] = PySide # HACK for ImageQt

import Image
import ImageQt

from eyefilinuxui.util import get_exif_tags, get_tags_to_show, how_much_rotate
from eyefilinuxui.gui.ui.mainwindow_ui import Ui_MainWindow


logger = logging.getLogger(__name__)


#
# To build:
#
# $ pyside-uic eyefilinuxui/gui/ui/mainwindow.ui > eyefilinuxui/gui/ui/mainwindow_ui.py
#

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        # Hold references to current image
        self.current_image_filename = None
        self.current_image = None
        self.current_image_qt = None
        self.current_pixmap = None
        self.current_image_rotate = 0 # How much (if any) to rotate the current image
        self.current_image_exif = {}

        # Hold references to thumbs
        self.thumbs = []

        self.scene = QtGui.QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.resize(800, 600)
        self.splitter.setSizes([600, 180])
        self.listWidgetThumbs.setIconSize(QtCore.QSize(100, 100))

        self.tableWidgetExif.verticalHeader().setResizeMode(QtGui.QHeaderView.Fixed)

        # Create thread and connect
        self.rabbitmq_reader_thread = RabbitMQEventReaderThread()
        self.rabbitmq_reader_thread.start()

        # self.clear_exif()
        self.update_exif(None)
        self._connect_signals()

    def resizeEvent(self, event):
        """Override `resizeEvent()`"""
        self._resize_current_image()

    def _connect_signals(self):
        """Connect the signals"""
        self.connect(self.rabbitmq_reader_thread,
            QtCore.SIGNAL("display_image(QString)"),
            self.display_image)

        self.connect(self.splitter,
            QtCore.SIGNAL("splitterMoved(int, int)"),
            self._resize_current_image)

        self.listWidgetThumbs.currentItemChanged.connect(
            self._show_image_from_thumbs)

    def _show_image_from_thumbs(self, current, previous):
        """Shows and image from the thumbnails"""
        img_list = self.thumbs[self.listWidgetThumbs.currentRow()]
        self.display_image(img_list[0], add_to_thumb_list=False)

    def _resize_current_image(self):
        if self.current_image:
            w, h = self.current_image.size
            self.graphicsView.fitInView(QtCore.QRectF(0, 0, w, h), QtCore.Qt.KeepAspectRatio)
            self.scene.update()

    def clear_exif(self):
        self.tableWidgetExif.clear()
        self.tableWidgetExif.setColumnCount(1)
        self.tableWidgetExif.setHorizontalHeaderLabels(["Value"])

        # FIXME: clean with one call (don't know how)
        while self.tableWidgetExif.rowCount():
            self.tableWidgetExif.removeRow(0)

    def update_exif(self, image_filename):
        """Updates the EXIF information, updates `image_rotate`"""
        self.clear_exif()
        self.current_image_rotate = 0
        if image_filename:
            self.current_image_exif = get_exif_tags(image_filename)
        else:
            self.current_image_exif = {}

        exif_dict_to_show = get_tags_to_show(self.current_image_exif)
        # exif_keys = exif_dict_to_show.keys()
        # for row_num in range(0, len(exif_dict_to_show)):
        row_num = 0
        for _, tag_value in exif_dict_to_show.iteritems():
            valueItem = QtGui.QTableWidgetItem()
            valueItem.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
            valueItem.setFlags(valueItem.flags() ^ QtCore.Qt.ItemIsEditable)
            valueItem.setText(unicode(tag_value))
            self.tableWidgetExif.insertRow(row_num)
            self.tableWidgetExif.setItem(row_num, 0, valueItem)
            row_num += 1

        self.tableWidgetExif.setVerticalHeaderLabels(exif_dict_to_show.keys())
        self.tableWidgetExif.resizeColumnsToContents()
        self.current_image_rotate = how_much_rotate(self.current_image_exif) or 0

    def add_current_image_to_thumb_list(self):
        thumb_item = QtGui.QListWidgetItem()
        icon = QtGui.QIcon(self.current_pixmap)
        thumb_item.setIcon(icon)
        self.listWidgetThumbs.addItem(thumb_item)
        self.thumbs.append(
            (self.current_image_filename, self.current_image, self.current_image_qt, self.current_pixmap, icon)
        )

    def display_image(self, image_filename, add_to_thumb_list=True):
        self.current_image_filename = image_filename
        self.current_image = Image.open(self.current_image_filename)
        self.scene.clear()
        self.graphicsView.resetTransform()
        self.graphicsView.resetMatrix()

        self.statusBar.showMessage("Image: {0}".format(self.current_image_filename))
        self.current_image_qt = ImageQt.ImageQt(self.current_image)
        self.current_pixmap = QtGui.QPixmap.fromImage(self.current_image_qt, QtCore.Qt.ImageConversionFlag.AutoColor)
        self.scene.addPixmap(self.current_pixmap)

        self.update_exif(self.current_image_filename)

        if self.current_image_rotate != 0:
            self.graphicsView.rotate(self.current_image_rotate) # update_exif() updates `image_rotate`

        if add_to_thumb_list:
            self.add_current_image_to_thumb_list()

        self._resize_current_image()


def start_gui():
    """
    Creates the QApplication and window.
    Returns (app, window,), you must call `app.exec_()`.
    """
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app, window


if __name__ == '__main__':
    app, window = start_gui()
    sys.exit(app.exec_())
