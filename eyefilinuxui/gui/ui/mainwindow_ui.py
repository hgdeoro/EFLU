# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'eyefilinuxui/gui/ui/mainwindow.ui'
#
# Created: Mon Mar  4 20:54:29 2013
#      by: pyside-uic 0.2.13 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(606, 477)
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
        self.tableWidgetExif.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tableWidgetExif.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tableWidgetExif.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tableWidgetExif.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tableWidgetExif.setShowGrid(False)
        self.tableWidgetExif.setWordWrap(False)
        self.tableWidgetExif.setRowCount(5)
        self.tableWidgetExif.setColumnCount(1)
        self.tableWidgetExif.setObjectName("tableWidgetExif")
        self.tableWidgetExif.setColumnCount(1)
        self.tableWidgetExif.setRowCount(5)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetExif.setItem(0, 0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetExif.setItem(1, 0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetExif.setItem(2, 0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetExif.setItem(3, 0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetExif.setItem(4, 0, item)
        self.tableWidgetExif.verticalHeader().setVisible(False)
        self.verticalLayout_2.addWidget(self.tableWidgetExif)
        self.tabWidget.addTab(self.tabExif, "")
        self.tabStatus = QtGui.QWidget()
        self.tabStatus.setObjectName("tabStatus")
        self.formLayout = QtGui.QFormLayout(self.tabStatus)
        self.formLayout.setObjectName("formLayout")
        self.status_label_rabbitmq = QtGui.QLabel(self.tabStatus)
        self.status_label_rabbitmq.setObjectName("status_label_rabbitmq")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.status_label_rabbitmq)
        self.status_checkBox_rabbitmq = QtGui.QCheckBox(self.tabStatus)
        self.status_checkBox_rabbitmq.setEnabled(False)
        self.status_checkBox_rabbitmq.setObjectName("status_checkBox_rabbitmq")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.status_checkBox_rabbitmq)
        self.status_checkBox_hostapd = QtGui.QCheckBox(self.tabStatus)
        self.status_checkBox_hostapd.setEnabled(False)
        self.status_checkBox_hostapd.setObjectName("status_checkBox_hostapd")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.status_checkBox_hostapd)
        self.status_label_hostapd = QtGui.QLabel(self.tabStatus)
        self.status_label_hostapd.setObjectName("status_label_hostapd")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.status_label_hostapd)
        self.status_checkBox_udhcpd = QtGui.QCheckBox(self.tabStatus)
        self.status_checkBox_udhcpd.setEnabled(False)
        self.status_checkBox_udhcpd.setObjectName("status_checkBox_udhcpd")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.status_checkBox_udhcpd)
        self.status_label_udhcpd = QtGui.QLabel(self.tabStatus)
        self.status_label_udhcpd.setObjectName("status_label_udhcpd")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.status_label_udhcpd)
        self.status_label_eyefiserver2 = QtGui.QLabel(self.tabStatus)
        self.status_label_eyefiserver2.setObjectName("status_label_eyefiserver2")
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.status_label_eyefiserver2)
        self.status_checkBox_eyefiserver2 = QtGui.QCheckBox(self.tabStatus)
        self.status_checkBox_eyefiserver2.setEnabled(False)
        self.status_checkBox_eyefiserver2.setObjectName("status_checkBox_eyefiserver2")
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.status_checkBox_eyefiserver2)
        self.tabWidget.addTab(self.tabStatus, "")
        self.listWidgetThumbs = QtGui.QListWidget(self.splitter_2)
        self.listWidgetThumbs.setMaximumSize(QtCore.QSize(16777215, 100))
        self.listWidgetThumbs.setFlow(QtGui.QListView.LeftToRight)
        self.listWidgetThumbs.setObjectName("listWidgetThumbs")
        self.gridLayout.addWidget(self.splitter_2, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtGui.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 606, 21))
        self.menuBar.setObjectName("menuBar")
        self.menuFile = QtGui.QMenu(self.menuBar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtGui.QToolBar(MainWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtGui.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.action_Quit = QtGui.QAction(MainWindow)
        self.action_Quit.setObjectName("action_Quit")
        self.menuFile.addAction(self.action_Quit)
        self.menuBar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QObject.connect(self.action_Quit, QtCore.SIGNAL("activated()"), MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "EyeFiLinuxUi", None, QtGui.QApplication.UnicodeUTF8))
        __sortingEnabled = self.tableWidgetExif.isSortingEnabled()
        self.tableWidgetExif.setSortingEnabled(False)
        self.tableWidgetExif.item(0, 0).setText(QtGui.QApplication.translate("MainWindow", "abc", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidgetExif.item(1, 0).setText(QtGui.QApplication.translate("MainWindow", "abc", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidgetExif.item(2, 0).setText(QtGui.QApplication.translate("MainWindow", "abc", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidgetExif.item(3, 0).setText(QtGui.QApplication.translate("MainWindow", "abc", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidgetExif.item(4, 0).setText(QtGui.QApplication.translate("MainWindow", "abc", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidgetExif.setSortingEnabled(__sortingEnabled)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabExif), QtGui.QApplication.translate("MainWindow", "Exif", None, QtGui.QApplication.UnicodeUTF8))
        self.status_label_rabbitmq.setText(QtGui.QApplication.translate("MainWindow", "UNKNOWN", None, QtGui.QApplication.UnicodeUTF8))
        self.status_checkBox_rabbitmq.setText(QtGui.QApplication.translate("MainWindow", "RabbitMQ", None, QtGui.QApplication.UnicodeUTF8))
        self.status_checkBox_hostapd.setText(QtGui.QApplication.translate("MainWindow", "HostAPd", None, QtGui.QApplication.UnicodeUTF8))
        self.status_label_hostapd.setText(QtGui.QApplication.translate("MainWindow", "UNKNOWN", None, QtGui.QApplication.UnicodeUTF8))
        self.status_checkBox_udhcpd.setText(QtGui.QApplication.translate("MainWindow", "uDHCPd", None, QtGui.QApplication.UnicodeUTF8))
        self.status_label_udhcpd.setText(QtGui.QApplication.translate("MainWindow", "UNKNOWN", None, QtGui.QApplication.UnicodeUTF8))
        self.status_label_eyefiserver2.setText(QtGui.QApplication.translate("MainWindow", "UNKNOWN", None, QtGui.QApplication.UnicodeUTF8))
        self.status_checkBox_eyefiserver2.setText(QtGui.QApplication.translate("MainWindow", "EyeFiServer2", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabStatus), QtGui.QApplication.translate("MainWindow", "Status", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Quit.setText(QtGui.QApplication.translate("MainWindow", "&Quit", None, QtGui.QApplication.UnicodeUTF8))

