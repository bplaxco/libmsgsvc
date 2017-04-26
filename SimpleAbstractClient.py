#! /usr/bin/env python

import thread
import time

from MessageBus import MessageBus


def default_main(bus):
    time.sleep(60 * 60 * 24 * 365 * 100)


class SimpleAbstractClient(object):
    def __init__(self, client_id, password, receiver, main=default_main, server="irc.freenode.net:6667", debug=False):
        self.bus = MessageBus("irc://%s:%s@%s" % (client_id, password, server), debug=debug)
        self.main = main
        thread.start_new_thread(self._start_handler, (receiver,))

    def begin(self):
        while True:
            self.main(self)

    def send(self, data):
        self.bus.send_data(data)

    def _start_handler(self, receiver):
        while not self.bus.is_ready():
            pass

        while True:
            receiver(self.bus, self.bus.recv())
