#!/usr/bin/env python
import json
import sys

from SimpleAbstractClient import SimpleAbstractClient


def receive(bus, msg):
    print(msg.get_data())


def main(bus):
    value = raw_input().strip()

    if value == "exit":
        sys.exit(0)

    try:
        bus.send_data(json.loads(value))
    except:
        bus.send_data(value)


SimpleAbstractClient("sclient", "password", receive, main, server="localhost:6667", debug=False).begin()
