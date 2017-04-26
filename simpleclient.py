#!/usr/bin/env python

from simpleabstractclient import SimpleAbstractClient

def receive(bus, msg):
    print(msg)

def main(bus):
    bus.send(raw_input().strip())

SimpleAbstractClient("simple-client", "password", receive, main).begin()
