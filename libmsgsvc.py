from simplecrypt import encrypt, decrypt

import base64
import hashlib
import json
import os
import random
import socket
import sys
import time
import uuid
import thread


class MsgService(object):
    def __init__(self, server, password, nick, port=6667, debug=False):
        self.debug = debug
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.channel = '#' + hashlib.sha256(password).hexdigest()[:25]
        self.password = password
        self.msg_ids = []
        self.conn.connect((server, port))
        self.nick = nick

    def join(self):
        self.send("USER %s %s %s : " % (self.nick, self.nick, self.nick))
        self.send("NICK %s" % self.nick)
        self.send("JOIN %s" % self.channel)

    def send(self, msg):
        if self.debug: print("<- " + msg)
        self.conn.send(msg + "\r\n")

    def recv(self):
        #TODO: figure out how to handle chunked messages
        text = self.conn.recv(2 ** 14)
        if self.debug: print("-> " + text)
        return text

    def send_message(self, data):
        msg = json.dumps({"id": str(uuid.uuid4()), "data": data})
        msg = base64.b64encode(encrypt(self.password, msg))
        self.send("PRIVMSG %s MSGSVC%s" % (self.channel, msg))

    def recv_message(self):
        text = self.recv()

        if not text:
            return

        if text.find('PING') != -1:
            msg = 'PONG ' + text.split()[1]
            self.send(msg)
        elif "MSGSVC" in text:
            parts = text.split("PRIVMSG %s :" % self.channel)
            if len(parts) > 1:
                msg = parts[1].split("MSGSVC")[1]
                msg = decrypt(self.password, base64.b64decode(msg)).strip()

                try:
                    msg = json.loads(msg)
                    msg_id = msg["id"]
                    msg_data = msg["data"]

                    # TODO: store these somewhere else
                    if msg_id not in self.msg_ids:
                        self.msg_ids.append(msg_id)
                        return msg_data
                except:
                    pass


def on_recv(svc, handler):
    def _start():
        while True:
            msg = svc.recv_message()
            if msg:
                handler(svc, msg)

    return thread.start_new_thread(_start, tuple())
