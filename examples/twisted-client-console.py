#!/usr/bin/env python
from twisted.cred import credentials
from twisted.internet import reactor
from parseltone.interface.client.base import Client
from parseltone.interface.client.curses import prompt_credentials
from parseltone.utils import log


# create a log target for this module
logger = log.logging.getLogger(__name__)


class ExampleClient(Client):
    def get_credentials(self):
        username, password = prompt_credentials()
        return credentials.UsernamePassword(username, password)


if __name__ == '__main__':
    client = ExampleClient()
    client.connect('localhost:8800')
    reactor.run()

