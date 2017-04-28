#!/usr/bin/env python
import json
import sys

from libmsgsvc.SimpleClient import SimpleClient


def receive(bus):
    print(bus.recv().get_data())


def main(bus):
    value = raw_input().strip()

    if value == "exit":
        sys.exit(0)

    try:
        bus.send_data(json.loads(value))
    except:
        bus.send_data(value)


if __name__ == "__main__":
    client = SimpleClient("irc://sclient:password@irc.freenode.net:6667")
    client.non_blocking_loop(receive)
    client.loop(main)
