#! /usr/bin/env python

import signal
import thread
import time

from busses.MessageBus import MessageBus
from Message import Message


class AbstractClient(object):
    @classmethod
    def freenode_connect(cls, client_id, channel, debug=False):
        return cls(
            "irc://%s:%s@irc.freenode.net:6667" % (client_id, channel),
             debug=debug,
        )

    def __init__(self, connection_str, debug=False):
        self._bus = MessageBus(connection_str, debug=debug)

        while not self._bus.is_ready():
            time.sleep(1)

        thread.start_new_thread(self.__listen, ())
        thread.start_new_thread(self.__publish, ())

    def __listen(self):
        while True:
            self.listen(self._bus.recv())

    def __publish(self):
        while True:
            self.publish()

    def create_message(self, data):
        """So that the user doesn't have to touch the message object"""
        return Message(self.get_client_id(), data)

    def get_bus(self):
        return self._bus

    def get_client_id(self):
        return self._bus.get_client_id()

    def listen(self, message):
        raise NotImplementedError

    def publish(self):
        raise NotImplementedError

    def pause(self):
        signal.pause()
