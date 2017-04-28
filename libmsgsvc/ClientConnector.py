#! /usr/bin/env python

from Queue import Queue

import signal
import thread
import time

from busses.MessageBus import MessageBus


class ClientConnector(object):

    _listener_queues = None

    @classmethod
    def irc_connect(cls, client_id, channel, debug=False):
        return cls("irc://%s:%s@irc.freenode.net:6667" % (client_id, channel), debug)

    def __init__(self, connection_str, debug=False):
        self._bus = MessageBus(connection_str, debug=debug)
        self._wait_for_bus()
        self._listener_queues = []
        thread.start_new_thread(self._start_proxy_listener, ())

    def _start_proxy_listener(self):
        while True:
            self._proxy_listener(self._bus.recv())

    def _proxy_listener(self, msg):
            for q in self._listener_queues:
                q.put(msg)

    def _wait_for_bus(self):
        while not self._bus.is_ready():
            time.sleep(1)

    def listen(self, method, loop=True, foreground=False):
        if not foreground:
            thread.start_new_thread(self.listen, (method, loop, True))
        else:
            q = Queue()
            self._listener_queues.append(q)
            method(self._bus, q.get())
            while loop:
                method(self._bus, q.get())

        return self

    def publish(self, method, loop=True, foreground=False):
        if not foreground:
            thread.start_new_thread(self.publish, (method, loop, True))
        else:
            method(self._bus)
            while loop:
                method(self._bus)
        return self

    def hang(self):
        signal.pause()


