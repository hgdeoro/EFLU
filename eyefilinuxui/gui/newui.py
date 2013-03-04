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

from eyefilinuxui.util import get_exif_tags
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
        self.image = None
        self.imageQt = None
        self.pixMap = None

        # How much (if any) to rotate the current image
        self.image_rotate = 0

        # Hold references to thumbs
        self.thumbs = []

        self.scene = QtGui.QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.resize(800, 600)
        self.splitter.setSizes([600, 180])
        self.listWidgetThumbs.setIconSize(QtCore.QSize(100, 100))

        # Create thread and connect
        self.rabbitmq_reader_thread = RabbitMQEventReaderThread()
        self.rabbitmq_reader_thread.start()

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
        if self.image:
            w, h = self.image.size
            self.graphicsView.fitInView(QtCore.QRectF(0, 0, w, h), QtCore.Qt.KeepAspectRatio)
            self.scene.update()

    def update_exif(self, image_filename):
        """Updates the EXIF information, updates `image_rotate`"""
        self.tableWidgetExif.clear()
        self.tableWidgetExif.setColumnCount(1)
        self.tableWidgetExif.setHorizontalHeaderLabels(["Value"])
        self.image_rotate = 0

        # FIXME: clean with one call (don't know how)
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

    def add_current_image_to_thumb_list(self):
        thumb_item = QtGui.QListWidgetItem()
        icon = QtGui.QIcon(self.pixMap)
        thumb_item.setIcon(icon)
        self.listWidgetThumbs.addItem(thumb_item)
        self.thumbs.append(
            (self.current_image_filename, self.image, self.imageQt, self.pixMap, icon)
        )

    def display_image(self, image_filename, add_to_thumb_list=True):
        self.current_image_filename = image_filename
        self.image = Image.open(self.current_image_filename)
        self.scene.clear()
        self.graphicsView.resetTransform()
        self.graphicsView.resetMatrix()

        self.statusBar.showMessage("Image: {0}".format(self.current_image_filename))
        self.imageQt = ImageQt.ImageQt(self.image)
        self.pixMap = QtGui.QPixmap.fromImage(self.imageQt, QtCore.Qt.ImageConversionFlag.AutoColor)
        self.scene.addPixmap(self.pixMap)

        self.update_exif(self.current_image_filename)

        if self.image_rotate != 0:
            self.graphicsView.rotate(self.image_rotate) # update_exif() updates `image_rotate`

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
