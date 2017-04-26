#!/usr/bin/env python

from simpleabstractclient import SimpleAbstractClient

def receive(bus, msg):
    print(msg["data"])

def main(bus):
    bus.send_message(raw_input("Text: ").strip())

SimpleAbstractClient("simple-client", "password", receive, main, debug=False).begin()
