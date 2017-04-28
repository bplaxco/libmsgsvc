#!/usr/bin/env python

import ClientConnector
from time import sleep

count=0

def receive(bus, msg):
    print("Got "+msg.get_data())

def receive_caps(bus, msg):
    print("In caps that's "+msg.get_data().upper())

def main(bus):
    bus.send_data(raw_input(">").strip())

def tick(bus):
    global count
    sleep(10)
    count+=10
    bus.send_data(str(count)+" seconds have passed.")


bus = ClientConnector.login("client", "password")
bus.listen(receive)
bus.listen(receive_caps)
bus.publish(tick)
bus.publish(main, foreground=True)
