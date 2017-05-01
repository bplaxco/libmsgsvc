#!/usr/bin/env python

from libmsgsvc.AbstractClient import AbstractClient
import json


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


client = Client("password", tracker="localhost:5556", debug=True)
client.pause()
