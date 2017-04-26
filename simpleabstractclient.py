#! /usr/bin/env python

from libmsgsvc import svc_connect, svc_on_recv
import sys
import time


def print_handler(svc, msg):
    print(msg["data"])

class SimpleAbstractClient(object):

    svc=None
    main=None

    def dummymain(self):
        time.sleep(60*60*24*365*100)

    def  __init__(self, user, channel, recv_handler, main=dummymain):
        info="irc://"+user+":"+channel+"@irc.freenode.net:6667"
        self.svc = svc_connect(info, debug=True)
        svc_on_recv(self.svc, recv_handler)
        time.sleep(2)
        self.svc.join()
        self.main=main


    def begin(self):
        while True:
            self.main(self)

    def send(self, msg):
        svc.send_message(msg)