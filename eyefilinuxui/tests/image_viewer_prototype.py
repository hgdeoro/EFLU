#!/usr/bin/env python
# -*- coding: utf-8 -*-

# http://stackoverflow.com/questions/8766584/displayin-an-image-in-a-qgraphicsscene

import sys

import Image
import ImageQt

from PyQt4.QtCore import * #@UnusedWildImport
from PyQt4.QtGui import * #@UnusedWildImport


image_name = sys.argv[1]


class TestWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.button = QPushButton("Test")

        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.view)
        self.setLayout(layout)

    def _do_resize(self):
        self.view.fitInView(QRectF(0, 0, self._w, self._h), Qt.KeepAspectRatio)
        self.scene.update()

    def resizeEvent(self, event):
        self._do_resize()

    def display_image(self):
        self._img = Image.open(image_name)
        self.scene.clear()
        self._w, self._h = self._img.size
        self.imgQ = ImageQt.ImageQt(self._img) # we need to hold reference to imgQ, or it will crash
        self._pixMap = QPixmap.fromImage(self.imgQ)
        self.scene.addPixmap(self._pixMap)
        self.view.fitInView(QRectF(0, 0, self._w, self._h), Qt.KeepAspectRatio)
        self.scene.update()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = TestWidget()
    widget.display_image()
    widget.show()

    sys.exit(app.exec_())
