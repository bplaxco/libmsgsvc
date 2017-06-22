#! /usr/bin/env python

import json
import sys

from libmsgsvc.AbstractClient import AbstractClient


class Client(AbstractClient):
    def on_recv(self, data):
        print(data)


if __name__ == "__main__":
    debug = False
    server = "irc.freenode.net:6667"
    server = "localhost:6667"

    if len(sys.argv) == 1:
        client = Client("public", server=server, debug=debug)
    elif len(sys.argv) == 2:
        client = Client(sys.argv[1], server=server, debug=debug)
    elif len(sys.argv) > 2:
        client = Client(sys.argv[1], server=sys.argv[2], debug=debug)

    while True:
        client.send(raw_input("(%s in room) > " % client.get_subscriber_count()).strip())
