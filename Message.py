import json
import time
import uuid

from ciphers import AESCipher


class Message(object):
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

    @classmethod
    def from_dict(cls, msg_dict):
        return cls(**msg_dict)

    def to_encrypted_str(self, password):
        return AESCipher(password).encrypt(json.dumps(self.to_dict()))

    @classmethod
    def from_encrypted_str(cls, password, encrypted_str):
        return cls.from_dict(json.loads(AESCipher(password).decrypt(encrypted_str)))

    def get_data(self):
        return self._data

    def get_id(self):
        return self._id

    def get_client_id(self):
        return self._client_id

    def get_created_at(self):
        return self._created_at

