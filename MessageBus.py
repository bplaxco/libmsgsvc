from Queue import Queue
import hashlib
import thread
import time

from Message import Message
from connectors.IRCConnector import IRCConnector


class MessageBus(object):
    _connector_by_proto = {"irc": IRCConnector}
    _password = "public"
    _connector = None

    def __init__(self, connect_string, debug=False):
        """
        connect_string format: irc://client_type:password@server:port
        """
        proto, client_id, password, server, port = self._parse_connect_string(connect_string)
        Connector = self._connector_class_by_proto(proto)
        channel = '#' + hashlib.sha256(password).hexdigest()[:25]  # @UndefinedVariable

        print("Channel: " + channel)

        self._client_id = ("%s-%s" % (client_id, hashlib.sha256(str(time.time())).hexdigest()[:5]))[:16]  # @UndefinedVariable
        self._send_queue = Queue()
        self._recv_queue = Queue()
        self._connector = Connector(self._client_id, channel, server, port, debug=debug)
        self._password = password

        # Start send and receive threads and join
        thread.start_new_thread(self._queue_recv, tuple())
        thread.start_new_thread(self._dequeue_send, tuple())

    def _parse_connect_string(self, connect_string):
        proto, user_server_info = connect_string.split("://")
        user_info, server_info = user_server_info.split("@")
        client_id, password = user_info.split(":")
        server, port = server_info.split(":")
        return proto, client_id, password, server, port

    def _connector_class_by_proto(self, proto):
        try:
            return self._connector_by_proto[proto]
        except:
            raise Exception("%s is not supported" % proto)

    def _queue_recv(self):
        while True:
            text = self._connector.recv()
            if "MSGSVC" in text:
                encrypted_str = text.split("MSGSVC")[1]
                message = Message.from_encrypted_str(self._password, encrypted_str)
                self._recv_queue.put(message)

    def _dequeue_send(self):
        while not self.is_ready():
            pass

        print("READY")

        while True:
            self._connector.send("MSGSVC" + self._send_queue.get().to_encrypted_str(self._password))

    def send(self, message):
        self._send_queue.put(message)

    def send_data(self, data):
        self.send(Message(self._client_id, data))

    def recv(self):
        return self._recv_queue.get()

    def recv_data(self):
        return self.recv().get_data()

    def is_ready(self):
        return self._connector.is_ready()

    def close(self):
        self._connector.close()

