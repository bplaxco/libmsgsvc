#! /usr/bin/env python

import json
import sys

from libmsgsvc.AbstractClient import AbstractClient


class Client(AbstractClient):
    def listen(self, msg):
        print(msg.get_data())

    def publish(self):
        data = raw_input("> ").strip()

        try:
            self.get_bus().send_data(json.loads(data))
        except:
            self.get_bus().send_data(data)

        # Example using create_message
        # try:
        #     message = self.create_message(json.loads(data))
        # except:
        #     message = self.create_message(data)
        #
        # self.get_bus().send(message)


if len(sys.argv) == 1:
    client = Client("public", tracker="localhost:5556")
elif len(sys.argv) == 2:
    client = Client(sys.argv[1], tracker="localhost:5556")
elif len(sys.argv) > 2:
    client = Client(sys.argv[1], tracker=sys.argv[2])

client.pause()
