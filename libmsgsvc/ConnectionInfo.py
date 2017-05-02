import hashlib
import random
import socket
import string
import uuid


class ConnectionInfo(object):
    def __init__(self, secret_key, tracker):
        self._secret_key = secret_key
        self._tracker = tracker
        self._channel = '#' + hashlib.sha256(secret_key).hexdigest()[:25]

        # Some servers don't like it if you start with a number
        self._client_id = random.choice(string.letters)
        self._client_id += hashlib.sha256(str(uuid.uuid4())).hexdigest()[:8]

    def get_channel(self):
        return self._channel

    def get_client_id(self):
        return self._client_id

    def get_secret_key(self):
        return self._secret_key

    def get_server_and_port(self):
        try:
            server, port = self._tracker.split(":")
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((server, int(port)))
            conn.send("REQSVR %s" % self.get_channel())
            server, port = conn.recv(1024).split(":")
            return (server, int(port))
        except:
            print("Tracker Error: using default server and port... (irc.freenode.net:6667)")
            return ("irc.freenode.net", 6667)

    def __str__(self):
        server, port = self.get_server_and_port()
        return "Connecting to %s:%d on %s as %s" % (server, port, self.get_channel(), self._client_id)
