#! /usr/bin/env python

import thread
import signal
import time

from busses.MessageBus import MessageBus

class AbstractClient(object):
    reciever=None
    main=None

    def __init__(self, client_id, password, reciever, main=None, server="irc.freenode.net:6667", debug=False):
        self.bus = MessageBus("irc://%s:%s@%s" % (client_id, password, server), debug=debug)
        self.reciever = reciever
        self.main = main

    def _wait_for_bus(self):
        while not self.bus.is_ready():
            time.sleep(1)

    def listen(self, loop=True, foreground=False):
        self._wait_for_bus()
        if not foreground:
            thread.start_new_thread(self.listen, (loop, True))
        else:
            self.reciever(self.bus, self.bus.recv())
            while loop:
                self.reciever(self.bus, self.bus.recv())
        return self

    def push(self, loop=True, foreground=True):
        self._wait_for_bus()
        if not foreground:
            thread.start_new_thread(self.push, (loop, True))
        else:
            self.main(self.bus)
            while loop:
                self.main(self.bus)
        return self

    def hang(self):
        signal.pause()
