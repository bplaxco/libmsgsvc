#! /usr/bin/env python

from Crypto import Random
from Crypto.Cipher import AES
from libmsgsvc.IRCConnector import IRCConnector
import base64
import hashlib
import json
import random
import string
import time
import uuid


MSG_PROTO = {"message_id": "", "data": {}, "client_id": "", "created_at": 0}
MSG_TAG = "MSGSVC-0.0.1-"


def merge_dicts(*dicts):
    return reduce(lambda a, d: a.update(d) or a, dicts, {})


def pad(s, bs):
    return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)


def unpad(s):
    return s[:-ord(s[len(s) - 1:])]


def sha256(secret_key, fmt="digest"):
    return getattr(hashlib.sha256(secret_key.encode()), fmt)()


def encrypt(secret_key, raw, bs=256):
    raw = pad(raw, bs)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(sha256(secret_key), AES.MODE_CBC, iv)
    return base64.b64encode(iv + cipher.encrypt(raw))


def decrypt(secret_key, enc):
    enc = base64.b64decode(enc)
    iv = enc[:AES.block_size]
    cipher = AES.new(sha256(secret_key), AES.MODE_CBC, iv)
    raw = unpad(cipher.decrypt(enc[AES.block_size:]))
    return raw.decode('utf-8')


def cast(x, to=int):
    return to(x) if x.isdigit() else x


def create_message(client_id, data):
    return {
        "client_id": client_id,
        "created_at": time.time(),
        "data": data,
        "message_id":  str(uuid.uuid4()),
    }


def encrypt_message(secret_key, message):
    return encrypt(secret_key, json.dumps(message))


def decrypt_message(secret_key, encrypted_str):
    try:
        return merge_dicts(MSG_PROTO, json.loads(decrypt(secret_key, encrypted_str)))
    except Exception as e:
        print(e)
        return None


def message_from_str(client, text):
    return decrypt_message(
        client.get_secret_key(), text.split(MSG_TAG)[1]
    ) if MSG_TAG in text else None


def data_to_message_str(client, data):
    return MSG_TAG + encrypt_message(
        client.get_secret_key(), create_message(client.get_id(), data),
    )


def fmt_id(first, body, length=8):
    return first + sha256(str(body), "hexdigest")[:length]


class AbstractClient(object):
    def __init__(self, secret_key, server=None, debug=False):
        self._received = []
        self._secret_key = secret_key
        self._server = server or "localhost:6667"
        self._channel = '#' + sha256(secret_key, "hexdigest")[:25]
        self._id = fmt_id(random.choice(string.letters), uuid.uuid4())
        self._bus = IRCConnector(self, debug=debug)
        print("Ready")

    def send(self, data):
        self._bus.send(data_to_message_str(self, data))

    def on_recv(self, msg):
        raise NotImplementedError

    def recv(self, text):
        msg = message_from_str(self, text)
        if msg and msg["message_id"] not in self._received:
            self._received.append(msg["message_id"])
            self.on_recv(msg["data"])

    def get_secret_key(self):
        return self._secret_key

    def get_id(self):
        return self._id

    def get_channel(self):
        return self._channel

    def get_server_and_port(self):
        return tuple(map(cast, self._server.split(":")))

    def get_subscriber_count(self):
        return self._bus.get_subscriber_count()
