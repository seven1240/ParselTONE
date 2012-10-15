# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'twisted-client-gui.ui'
#
# Created: Tue Jan 18 16:20:43 2011
#      by: PySide uic UI code generator
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(436, 138)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setAutoFillBackground(False)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 10, 421, 101))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.username_label = QtGui.QLabel(self.gridLayoutWidget)
        self.username_label.setEnabled(False)
        self.username_label.setObjectName("username_label")
        self.gridLayout.addWidget(self.username_label, 0, 1, 1, 1)
        self.username_edit = QtGui.QLineEdit(self.gridLayoutWidget)
        self.username_edit.setEnabled(False)
        self.username_edit.setObjectName("username_edit")
        self.gridLayout.addWidget(self.username_edit, 0, 2, 1, 1)
        self.password_label = QtGui.QLabel(self.gridLayoutWidget)
        self.password_label.setEnabled(False)
        self.password_label.setObjectName("password_label")
        self.gridLayout.addWidget(self.password_label, 1, 1, 1, 1)
        self.password_edit = QtGui.QLineEdit(self.gridLayoutWidget)
        self.password_edit.setEnabled(False)
        self.password_edit.setEchoMode(QtGui.QLineEdit.Password)
        self.password_edit.setObjectName("password_edit")
        self.gridLayout.addWidget(self.password_edit, 1, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(128, 48, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 0, 2, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(0, -1, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.closeButton = QtGui.QPushButton(self.gridLayoutWidget)
        self.closeButton.setObjectName("closeButton")
        self.horizontalLayout.addWidget(self.closeButton)
        self.loginButton = QtGui.QPushButton(self.gridLayoutWidget)
        self.loginButton.setEnabled(False)
        self.loginButton.setFlat(False)
        self.loginButton.setObjectName("loginButton")
        self.horizontalLayout.addWidget(self.loginButton)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.closeButton, QtCore.SIGNAL("clicked()"), MainWindow.close)
        QtCore.QObject.connect(self.username_edit, QtCore.SIGNAL("textChanged(QString)"), MainWindow.username_edit_textChanged)
        QtCore.QObject.connect(self.password_edit, QtCore.SIGNAL("textChanged(QString)"), MainWindow.password_edit_textChanged)
        QtCore.QObject.connect(self.password_edit, QtCore.SIGNAL("editingFinished()"), MainWindow.password_edit_editingFinished)
        QtCore.QObject.connect(self.username_edit, QtCore.SIGNAL("editingFinished()"), MainWindow.username_edit_editingFinished)
        QtCore.QObject.connect(self.loginButton, QtCore.SIGNAL("clicked()"), MainWindow.loginButton_clicked)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.username_label.setText(QtGui.QApplication.translate("MainWindow", "Username", None, QtGui.QApplication.UnicodeUTF8))
        self.password_label.setText(QtGui.QApplication.translate("MainWindow", "Password", None, QtGui.QApplication.UnicodeUTF8))
        self.closeButton.setText(QtGui.QApplication.translate("MainWindow", "Close", None, QtGui.QApplication.UnicodeUTF8))
        self.loginButton.setText(QtGui.QApplication.translate("MainWindow", "Login", None, QtGui.QApplication.UnicodeUTF8))

