#! /usr/bin/env python

import signal
import thread
import time

from busses.MessageBus import MessageBus
from Message import Message
from ConnectionInfo import ConnectionInfo


class AbstractClient(object):
    def __init__(self, secret_key, tracker="tracker.lupnix.org:5556", debug=False):
        self._connection_info = ConnectionInfo(secret_key, tracker)
        self._bus = MessageBus(self._connection_info, debug=debug)

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
        return self._connection_info.get_client_id()

    def get_channel(self):
        return self._connection_info.get_channel()

    def pause(self):
        signal.pause()

    def listen(self, message):
        raise NotImplementedError

    def publish(self):
        raise NotImplementedError

