import hashlib
import time

from AbstractBus import AbstractBus
from IRCConnector import IRCConnector
from libmsgsvc.Message import Message


class MessageBus(AbstractBus):
    _connector_by_proto = {"irc": IRCConnector}
    _password = "public"
    _connector = None
    _message_tag = "MSGSVC-%s-" % Message.version

    def __init__(self, connect_str, debug=False):
        """
        connect_str format: irc://client_type:password@server:port
        """
        super(MessageBus, self).__init__()
        proto, client_id, password, server, port = self._parse_connect_str(connect_str)
        Connector = self._connector_class_by_proto(proto)
        channel = '#' + hashlib.sha256(password).hexdigest()[:25]  # @UndefinedVariable
        self._client_id = ("%s-%s" % (client_id, hashlib.sha256(str(time.time())).hexdigest()[:5]))[:16]  # @UndefinedVariable
        self._connector = Connector(self._client_id, channel, server, port, debug=debug)
        self._password = password
        self._received_msg_ids = []
        self._start_queue_threads()

        print("Channel: " + channel)

    def _parse_connect_str(self, connect_str):
        proto, user_server_info = connect_str.split("://")
        user_info, server_info = user_server_info.split("@")
        client_id, password = user_info.split(":")
        server, port = server_info.split(":")
        return proto, client_id, password, server, int(port)

    def _connector_class_by_proto(self, proto):
        try:
            return self._connector_by_proto[proto]
        except:
            raise Exception("%s is not supported" % proto)

    def _queue_recv(self):
        while True:
            text = self._connector.recv()
            if self._message_tag in text:
                encrypted_str = text.split(self._message_tag)[1]
                message = Message.from_encrypted_str(self._password, encrypted_str)

                if message.get_id() in self._received_msg_ids:
                    continue

                self._received_msg_ids.append(message.get_id())
                self._recv_queue.put(message)

    def _dequeue_send(self):
        while not self.is_ready():
            time.sleep(1)

        print("READY")

        while True:
            self._connector.send(self._message_tag + self._send_queue.get().to_encrypted_str(self._password))

    def send_data(self, data):
        self.send(Message(self._client_id, data))

    def recv_data(self):
        return self.recv().get_data()

    def is_ready(self):
        return self._connector.is_ready()

    def close(self):
        self._connector.close()
