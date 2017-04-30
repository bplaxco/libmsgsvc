#!/usr/bin/env python

from MultiTennantConnector import MultiTennantConnector as mtc
from time import sleep

count = 0


def receive(bus, msg):
    print("Got " + msg.get_data())


def receive_caps(bus, msg):
    print("In caps that's " + msg.get_data().upper())


def main(bus):
    bus.send_data(raw_input(">").strip())


def tick(bus):
    global count
    sleep(10)
    count += 10
    bus.send_data(str(count) + " seconds have passed.")


con = mtc.freenode_connect("mtdc", "channel")
con.attach_listener(receive)
con.attach_listener(receive_caps)
con.attach_publisher(tick)
con.attach_publisher(main, foreground=True)
