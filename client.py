#!/usr/bin/env python

from AbstractClient import AbstractClient

def receive(bus, msg):
    print("Got "+msg.get_data())

def main(bus):
    bus.send_data(raw_input(">").strip())

bus = AbstractClient("client", "password").listen(receive).publish(main, foreground=True)
