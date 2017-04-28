#!/usr/bin/env python

import ClientConnector

def receive(bus, msg):
    print(msg.get_data())

def main(bus):
    bus.send_data(raw_input(">").strip())

bus = ClientConnector.connect("client", "password").listen(receive).publish(main, foreground=True)
