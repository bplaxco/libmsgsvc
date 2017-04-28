#!/usr/bin/env python

import ClientConnector
import json

def receive(bus, msg):
    print(msg.get_data())

def main(bus):
    data=raw_input(">").strip()
    try:
        data=json.loads(data)
        print "Got it."
    except:
        pass
    bus.send_data(data)

bus = ClientConnector.connect("dbc-clnt", "password").listen(receive).publish(main, foreground=True)
