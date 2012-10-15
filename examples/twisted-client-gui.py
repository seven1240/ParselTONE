#!/usr/bin/env python
import sys
from PySide.QtCore import *
from PySide.QtGui import *

# this odd import and code here is needed because twisted only allows 
## one reactor to be installed at a time, so we can't install the Qt 
## reactor after importing twisted.internet.reactor, which will install 
## a default reactor instead of the one we want here
app = QApplication(sys.argv) # your code to init Qt
from parseltone.interface.client.pyqt import qt4reactor
qt4reactor.install()

from twisted.cred import credentials
from twisted.internet import defer, reactor
from parseltone.interface.client.base import Client
from parseltone.utils import log

from twisted_client_gui_ui import Ui_MainWindow


# create a log target for this module
logger = log.logging.getLogger(__name__)


class MainWindow(QMainWindow, Ui_MainWindow):
    def closeEvent(self, event):
        """
        Stop the twisted reactor when this window is closed.
        """
        self.client.cleanup()
        reactor.stop()
        event.accept()

    def username_edit_textChanged(self, QString):
        """
        This slot triggered by the textChanged() signal on the 
        username_edit textarea.
        """
        if self.username_edit.text():
            self.enable_password()
        else:
            self.disable_password()
            self.disable_loginButton()

    def username_edit_editingFinished(self):
        """
        This slot triggered by the editingFinished() signal on the 
        username_edit textarea.
        """
        if self.username_edit.text():
            self.password_edit.setFocus()

    def password_edit_textChanged(self, QString):
        """
        This slot triggered by the textChanged() signal on the 
        password_edit textarea.
        """
        if self.password_edit.text():
            self.enable_loginButton()
        else:
            self.disable_loginButton()

    def password_edit_editingFinished(self):
        """
        This slot triggered by the editingFinished() signal on the 
        password_edit textarea.
        """
        if self.password_edit.text():
            self.loginButton.setFocus()

    def loginButton_clicked(self):
        """
        This slot triggered by the clicked() signal on the 
        loginButton button.
        """
        username = self.username_edit.text()
        password = self.password_edit.text()
        if not self.loginButton_deferred.called:
            self.loginButton_deferred.callback((username, password))

    def enable_loginButton(self):
        """
        Allow interaction with the loginButton button.
        """
        self.loginButton.setEnabled(True)

    def enable_username(self):
        """
        Allow interaction with the username textarea.
        """
        self.username_label.setEnabled(True)
        self.username_edit.setEnabled(True)

    def enable_password(self):
        """
        Allow interaction with the password textarea.
        """
        self.password_label.setEnabled(True)
        self.password_edit.setEnabled(True)

    def disable_loginButton(self):
        """
        Disable interaction with the loginButton button.
        """
        self.loginButton.setEnabled(False)

    def disable_username(self):
        """
        Disable interaction with the username textarea.
        """
        self.username_label.setEnabled(False)
        self.username_edit.setEnabled(False)

    def disable_password(self):
        """
        Disable interaction with the password textarea.
        """
        self.password_label.setEnabled(False)
        self.password_edit.setEnabled(False)


class ExampleClient(Client):
    def __init__(self):
        Client.__init__(self)
        self.mainwindow = MainWindow()
        self.mainwindow.client = self
        self.mainwindow.setupUi(self.mainwindow)

    def get_credentials(self):
        """
        Server has asked for credentials for the login process. This can
        return either the credentials, or a deferred whose callback must
        return the credentials.
        """
        self.mainwindow.statusBar().showMessage(
            'Server asked for username/password.')
        self.mainwindow.enable_username()

        self.mainwindow.loginButton_deferred = defer.Deferred()
        self.mainwindow.enable_username()
        self.mainwindow.enable_password()
        self.mainwindow.enable_loginButton()
        def got_credentials((username, password)):
            logger.info('Providing username/password to server.')
            self.mainwindow.disable_username()
            self.mainwindow.disable_password()
            self.mainwindow.disable_loginButton()
            return credentials.UsernamePassword(username, password)
        self.mainwindow.loginButton_deferred.addCallback(got_credentials)

        return self.mainwindow.loginButton_deferred

    def connected(self, perspective):
        """
        Client has connected to the server.
        """
        Client.connected(self, perspective)
        self.mainwindow.statusBar().showMessage('Logged in.')

    def login_failed(self, failure):
        """
        Client login has failed for some reason.
        """
        Client.login_failed(self, failure)
        self.mainwindow.statusBar().showMessage(
            'Failed: %s' % failure.getErrorMessage())

    def disconnected(self, reason):
        """
        Client has been disconnected from the server.
        """
        Client.disconnected(self, reason)
        self.mainwindow.statusBar().showMessage(
            'Disconnected: %s' % reason.getErrorMessage())

    def cleanup(self):
        """
        Perform any post-disconnect cleanup.
        """
        logger.info('Shutting down..')


if __name__ == '__main__':
    client = ExampleClient()
    client.mainwindow.show()
    client.connect('localhost:8800')

    # start twisted reactor
    reactor.run()

