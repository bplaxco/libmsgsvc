#!/usr/bin/env python

from libmsgsvc.ClientConnector import ClientConnector
import json


def receive(bus, msg):
    print(msg.get_data())


def main(bus):
    data = raw_input("> ").strip()

    try:
        bus.send_data(json.loads(data))
    except:
        bus.send_data(data)


connector = ClientConnector.irc_connect("dbc-clnt", "password")
connector.listen(receive).publish(main, foreground=True)
