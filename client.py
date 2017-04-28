#!/usr/bin/env python

from libmsgsvc import ClientConnector
import json

def receive(bus, msg):
    print(msg.get_data())

def main(bus):
    data=raw_input(">").strip()
    try:
        bus.send_data(json.loads(data))
    except:
        bus.send_data(data)

bus = ClientConnector.connect("dbc-clnt", "password").listen(receive).publish(main, foreground=True)
