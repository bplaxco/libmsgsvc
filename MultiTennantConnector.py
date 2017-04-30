#!/usr/bin/env python

from libmsgsvc.AbstractClient import AbstractClient
from Queue import Queue

import thread
import threading


class MultiTennantConnector(AbstractClient):
    _listener_queues = None
    _queue_list_lock = None

    def __init__(self, connection_str, debug=False):
        self._listener_queues = []
        self._queue_list_lock = threading.Lock()
        super(MultiTennantConnector, self).__init__(connection_str, debug)

    # This is our proxy listener, which will delegate to the queues of each
    # listener tennant
    def listen(self, msg):
        with self._queue_list_lock:
            for q in self._listener_queues:
                q.put(msg)

    # We want to attach new publishers, not use a unique existing one
    def publish(self):
        thread.exit()

    def attach_listener(self, method, loop=True, foreground=False):
        if not foreground:
            thread.start_new_thread(self.attach_listener, (method, loop, True))
        else:
            print "Attaching listener " + method.__name__
            q = Queue()

            with self._queue_list_lock:
                self._listener_queues.append(q)

            method(self.get_bus(), q.get())

            while loop:
                method(self.get_bus(), q.get())

        return self

    def attach_publisher(self, method, loop=True, foreground=False):
        if not foreground:
            thread.start_new_thread(
                self.attach_publisher,
                (method, loop, True),
            )
        else:
            print "Attaching publisher " + method.__name__
            method(self.get_bus())

            while loop:
                method(self.get_bus())

        return self
