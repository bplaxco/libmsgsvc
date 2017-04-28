#! /usr/bin/env python

import thread
import time

from busses.MessageBus import MessageBus


class SimpleClient(object):
    def __init__(self, connect_str, debug=False):
        self.bus = MessageBus(connect_str, debug=debug)

    def non_blocking_loop(self, f):
        thread.start_new_thread(self.loop, (f,))

    def loop(self, f):
        while not self.bus.is_ready():
            time.sleep(1)

        while True:
            f(self.bus)
