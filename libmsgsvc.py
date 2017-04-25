from simplecrypt import encrypt, decrypt

import base64
import hashlib
import json
import os
import random
import socket
import sys
import thread
import time
import uuid


def _print_signal(signal):
    print("Signal Emmited: (  ( (%s) )  )" % signal.title())


def svc_connect(connect_str, debug=False):
    """
    connect with irc://user:pass@server:port
    """
    proto, rest = connect_str.split("://")
    port = 6667

    if not proto == "irc":
        raise Exception("The only protocol supported right now is IRC")

    creds, server_info = rest.split("@")
    username, password = creds.split(":")
    server_info_parts = server_info.split(":")

    if len(server_info_parts) == 2:
        server, port = server_info_parts
        port = int(port)
    else:
        server = server_info_parts[0]

    return MsgService(server, password, username, port, debug=debug)


def svc_create_message(data, nick):
    return {"id": str(uuid.uuid4()), "data": data, "client": nick, "time": time.time()}


def svc_encode(password, msg):
    return base64.b64encode(encrypt(password, json.dumps(msg)))


def svc_decode(password, text):
    return json.loads(decrypt(password, base64.b64decode(text)))


def svc_start_handler(svc, handler):
    while True:
        msg = svc.recv_message()
        if msg:
            handler(svc, msg)


def svc_on_recv(svc, handler):
    return thread.start_new_thread(svc_start_handler, (svc, handler))


def irc_create_conn(server, port):
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((server, port))
    return conn


def irc_create_channel(password):
    return '#' + hashlib.sha256(password).hexdigest()[:25]


def irc_send(conn, msg, debug=False):
    if debug:
        print("<- " + msg)

    conn.send(msg + "\r\n")


def irc_recv(conn, debug=False):
    text = conn.recv(2 ** 14)
    if debug: print("-> " + text)
    return text


def irc_join(conn, channel, nick, debug=False):
    irc_send(conn, "USER %s %s %s : " % (nick, nick, nick), debug=debug)
    irc_send(conn, "NICK %s" % nick, debug=debug)
    irc_send(conn, "JOIN %s" % channel, debug=debug)


def irc_send_message(conn, to, password, data, nick, debug=False):
    msg = "PRIVMSG %s MSGSVC%s" % (to, svc_encode(password, svc_create_message(data, nick)))
    irc_send(conn, msg, debug=debug)


def irc_is_ready(nick, channel, text):
    """The server says that you've joined when you're good to go"""
    return nick in text and "JOIN" in text and channel in text


def irc_recv_message(conn, password, nick, channel, msg_ids, debug=False):
    text = irc_recv(conn, debug=debug) or ""

    if "MSGSVC" in text:
        try:
            msg = svc_decode(password, text.split("MSGSVC")[1])
            msg_id = msg["id"]

            if msg_id not in msg_ids:
                msg_ids.append(msg_id)
                return msg
        except:
            pass
    elif text.find('PING') != -1:
        msg = 'PONG ' + text.split()[1]
        irc_send(conn, msg)
    elif irc_is_ready(nick, channel, text):
        return svc_create_message({"__msgsvc.signal": "ready"}, nick)


class MsgService(object):
    """
    Wrap IRC service methods in easy to use object

    A MsgService must define three methods:
        join - join the chat room (usually after already connected)
        recv_message - return a raw msg object (see svc_create_message as an example)
        send_message - take msg data, create msg and send it
    """
    def __init__(self, server, password, nick, port, debug=False):
        self.channel = irc_create_channel(password)
        self.conn = irc_create_conn(server, port)
        self.debug = debug
        self.msg_ids = []
        self.nick = nick+"_"+hashlib.sha256(str(time.time())).hexdigest()[:5]
        self.password = password
        self.is_ready = False

    def join(self):
        irc_join(self.conn, self.channel, self.nick, debug=self.debug)

    def recv_message(self):
        msg = irc_recv_message(self.conn, self.password, self.nick, self.channel, self.msg_ids, debug=self.debug)
        signal = msg and msg["data"].get("__msgsvc.signal") or ""

        if signal:
            _print_signal(signal)

        if signal == "ready":
            self.is_ready = True
        else:
            return msg

    def send_message(self, data, to=None):
        irc_send_message(self.conn, to or self.channel, self.password, data, self.nick, debug=self.debug)
