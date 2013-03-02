'''
Created on Mar 2, 2013

@author: Horacio G. de Oro
'''

import sys
import Image
import ImageQt

from PyQt4 import QtCore, QtGui

from eyefilinuxui.gui.ui.mainwindow import Ui_MainWindow


class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QDialog.__init__(self)

        # Set up the user interface from Designer.
        self.setupUi(self)

        self.scene = QtGui.QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.graphicsView.setRenderHint(QtGui.QPainter.Antialiasing)

        self.scene.clear()
        img = Image.open(sys.argv[1])
        w, h = img.size
        self.imgQ = ImageQt.ImageQt(img)
        pixMap = QtGui.QPixmap.fromImage(self.imgQ)
        self.scene.addPixmap(pixMap)
        # Qt::KeepAspectRatio -> 1
        self.graphicsView.fitInView(QtCore.QRectF(0, 0, w, h), 1)
        self.scene.update()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
