import time

from AbstractBus import AbstractBus
from IRCConnector import IRCConnector
from libmsgsvc.Message import Message


class MessageBus(AbstractBus):
    _connector = None
    _message_tag = "MSGSVC-%s-" % Message.version

    def __init__(self, connection_info, debug=False):
        super(MessageBus, self).__init__()
        self._connection_info = connection_info
        self._connector = IRCConnector(connection_info, debug=debug)
        self._received_msg_ids = []
        self._start_queue_threads()

        print(str(connection_info))

    def _queue_recv(self):
        while True:
            text = self._connector.recv()
            if self._message_tag in text:
                encrypted_str = text.split(self._message_tag)[1]
                secret_key = self._connection_info.get_secret_key()
                message = Message.from_encrypted_str(secret_key, encrypted_str)

                if not message or message.get_id() in self._received_msg_ids:
                    continue

                self._received_msg_ids.append(message.get_id())
                self._recv_queue.put(message)

    def _dequeue_send(self):
        while not self.is_ready():
            time.sleep(1)

        print("READY")

        while True:
            secret_key = self._connection_info.get_secret_key()
            message = self._send_queue.get()
            encrypted_str = message.to_encrypted_str(secret_key)
            self._connector.send(self._message_tag + encrypted_str)

    def get_client_id(self):
        return self._connection_info.get_client_id()

    def send_data(self, data):
        self.send(Message(self.get_client_id(), data))

    def recv_data(self):
        return self.recv().get_data()

    def is_ready(self):
        return self._connector.is_ready()

    def close(self):
        self._connector.close()
