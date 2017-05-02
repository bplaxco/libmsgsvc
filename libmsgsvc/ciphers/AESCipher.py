import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES


class AESCipher(object):

    def __init__(self, secret_key):
        self.bs = 32
        self.secret_key = hashlib.sha256(secret_key.encode()).digest()

    def _pad(self, s):
        bs = self.bs
        return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)

    def _unpad(self, s):
        return s[:-ord(s[len(s) - 1:])]

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.secret_key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.secret_key, AES.MODE_CBC, iv)
        raw = self._unpad(cipher.decrypt(enc[AES.block_size:]))
        return raw.decode('utf-8')
