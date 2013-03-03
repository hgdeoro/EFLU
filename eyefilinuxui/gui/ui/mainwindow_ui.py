# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'eyefilinuxui/gui/ui/mainwindow.ui'
#
# Created: Sun Mar  3 20:02:21 2013
#      by: pyside-uic 0.2.13 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(606, 419)
        self.centralWidget = QtGui.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.gridLayout = QtGui.QGridLayout(self.centralWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter_2 = QtGui.QSplitter(self.centralWidget)
        self.splitter_2.setOrientation(QtCore.Qt.Vertical)
        self.splitter_2.setObjectName("splitter_2")
        self.splitter = QtGui.QSplitter(self.splitter_2)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.graphicsView = QtGui.QGraphicsView(self.splitter)
        self.graphicsView.setBaseSize(QtCore.QSize(800, 100))
        self.graphicsView.setObjectName("graphicsView")
        self.tabWidget = QtGui.QTabWidget(self.splitter)
        self.tabWidget.setMaximumSize(QtCore.QSize(300, 16777215))
        self.tabWidget.setBaseSize(QtCore.QSize(200, 100))
        self.tabWidget.setObjectName("tabWidget")
        self.tabExif = QtGui.QWidget()
        self.tabExif.setObjectName("tabExif")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.tabExif)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tableWidgetExif = QtGui.QTableWidget(self.tabExif)
        self.tableWidgetExif.setBaseSize(QtCore.QSize(200, 100))
        self.tableWidgetExif.setObjectName("tableWidgetExif")
        self.tableWidgetExif.setColumnCount(0)
        self.tableWidgetExif.setRowCount(0)
        self.verticalLayout_2.addWidget(self.tableWidgetExif)
        self.tabWidget.addTab(self.tabExif, "")
        self.listWidgetThumbs = QtGui.QListWidget(self.splitter_2)
        self.listWidgetThumbs.setMaximumSize(QtCore.QSize(16777215, 100))
        self.listWidgetThumbs.setFlow(QtGui.QListView.LeftToRight)
        self.listWidgetThumbs.setObjectName("listWidgetThumbs")
        self.gridLayout.addWidget(self.splitter_2, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtGui.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 606, 21))
        self.menuBar.setObjectName("menuBar")
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtGui.QToolBar(MainWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtGui.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabExif), QtGui.QApplication.translate("MainWindow", "Exif", None, QtGui.QApplication.UnicodeUTF8))

