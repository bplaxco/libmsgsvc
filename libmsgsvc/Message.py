import json
import time
import uuid

from ciphers.AESCipher import AESCipher


class Message(object):
    version = "0.0.1"  # Change if the message format changes

    @classmethod
    def from_dict(cls, msg_dict):
        return cls(**msg_dict)

    @classmethod
    def from_encrypted_str(cls, secret_key, encrypted_str):
        try:
            return cls.from_dict(json.loads(AESCipher(secret_key).decrypt(encrypted_str)))
        except:
            pass

    def __init__(self, client_id, data, message_id=None, created_at=None):
        self._client_id = client_id
        self._data = data
        self._id = message_id or str(uuid.uuid4())
        self._created_at = created_at or time.time()

    def to_dict(self):
        return {
            "message_id": self._id,
            "data": self._data,
            "client_id": self._client_id,
            "created_at": self._created_at,
        }

    def to_encrypted_str(self, secret_key):
        return AESCipher(secret_key).encrypt(json.dumps(self.to_dict()))

    def get_data(self):
        return self._data

    def get_id(self):
        return self._id

    def get_client_id(self):
        return self._client_id

    def get_created_at(self):
        return self._created_at
