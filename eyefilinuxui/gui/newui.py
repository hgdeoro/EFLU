'''
Created on Mar 2, 2013

@author: Horacio G. de Oro
'''

import sys
import Image
import ImageQt

from PyQt4 import QtCore, QtGui

from eyefilinuxui.gui.ui.mainwindow_ui import Ui_MainWindow


class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.scene = QtGui.QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.image = None
        self.imageQt = None
        self.pixMap = None

    def _do_resize(self):
        if self.image:
            w, h = self.image.size
            self.graphicsView.fitInView(QtCore.QRectF(0, 0, w, h), QtCore.Qt.KeepAspectRatio)
            self.scene.update()

    def resizeEvent(self, event):
        self._do_resize()

    def display_image(self, image_filename):
        self.image = Image.open(image_filename)
        self.imageQt = ImageQt.ImageQt(self.image)
        self.pixMap = QtGui.QPixmap.fromImage(self.imageQt)
        self.scene.clear()
        self.scene.addPixmap(self.pixMap)
        self._do_resize()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.display_image(sys.argv[1])
    sys.exit(app.exec_())
