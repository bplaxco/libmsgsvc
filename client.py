#!/usr/bin/env python

from SimpleAbstractClient import SimpleAbstractClient

def receive(bus, msg):
    print(msg)

def main(bus):
    bus.send(raw_input().strip())

SimpleAbstractClient("sclient", "password", receive, main).begin()
