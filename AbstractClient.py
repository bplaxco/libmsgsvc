#! /usr/bin/env python

from Queue import Queue
import signal
import thread
import time

from busses.MessageBus import MessageBus

class AbstractClient(object):

    listener_queues = None

    def __init__(self, client_id, password, server="irc.freenode.net:6667", debug=False):
        self.bus = MessageBus("irc://%s:%s@%s" % (client_id, password, server), debug=debug)
        self._wait_for_bus()
        self.listener_queues = []
        thread.start_new_thread(self._start_proxy_listener, ())

    def _start_proxy_listener(self):
        while True:
            self._proxy_listener(self.bus.recv())

    def _proxy_listener(self, msg):
            for q in self.listener_queues:
                q.put(msg)

    def _wait_for_bus(self):
        while not self.bus.is_ready():
            time.sleep(1)

    def listen(self, method, loop=True, foreground=False):
        if not foreground:
            thread.start_new_thread(self.listen, (method, loop, True))
        else:
            q = Queue()
            self.listener_queues.append(q)
            method(self.bus, q.get())
            while loop:
                method(self.bus, q.get())
        return self

    def publish(self, method, loop=True, foreground=False):
        if not foreground:
            thread.start_new_thread(self.publish, (method, loop, True))
        else:
            method(self.bus)
            while loop:
                method(self.bus)
        return self

    def hang(self):
        signal.pause()


# import signal
# import thread
#
# from libmsgsvc.busses.MessageBus import MessageBus
#
#
# class SimpleClient(object):
#     _is_listening = False
#     _bus = None
#
#     def __init__(connect_str, debug=False):
#         self._connect_str = connect_str
#         self._debug = debug
#         self._observers = []
#
#     def _notify(self, message):
#         for observer in self._observers:
#             thread.start_new_thread(observer, (self, message))
#
#     def _get_bus(self):
#         if not self._bus:
#             self._bus = MessageBus(self._connect_str, debug=self._debug)
#
#         return self._bus
#
#     def _listen(self):
#         while True:
#             self._notify(self._get_bus().recv())
#
#     def subscribe(self, observer):
#         self._observers.append(observer)
#         return self
#
#     def send(self, message):
#         self._notify(message)
#         self._get_bus().send(message)
#
#     def listen(self, blocking=False):
#         if not self._is_listening:
#             thread.start_new_thread(self._listen, tuple())
#             self._is_listening = True
#
#         if blocking:
#             signal.pause()
