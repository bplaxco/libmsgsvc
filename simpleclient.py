#!/usr/bin/env python

from simpleabstractclient import SimpleAbstractClient

def receive(bus, msg):
    print(msg)

bus=SimpleAbstractClient("simple-client", "password", receive)
bus.begin()
