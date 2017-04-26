#! /usr/bin/env python

from libmsgsvc import svc_connect, svc_on_recv
import sys
import time


def print_handler(svc, msg):
    print(msg["data"])

class SimpleAbstractClient(object):
    svc = None
    main = None

    def dummymain(self):
        time.sleep(60*60*24*365*100)

    def  __init__(self, user, channel, recv_handler, main=dummymain, debug=False, server="irc.freenode.net:6667"):
        info="irc://%s:%s@%s" % (user, channel, server)
        self.svc = svc_connect(info, debug)
        svc_on_recv(self.svc, recv_handler)
        time.sleep(2)
        self.svc.join()
        self.main = main

    def begin(self):
        print "Wait, connecting...."
        while not self.is_ready:
            time.sleep(1)
        print "Connected."
        while True:
            self.main(self)

    def send_message(self, msg):
        self.svc.send_message(msg)

    @property
    def is_ready(self):
        return self.svc.is_ready
