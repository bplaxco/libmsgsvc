import re
import socket
import time

from AbstractConnector import AbstractConnector


class IRCConnector(AbstractConnector):
    _privmsg_re = re.compile(".*PRIVMSG.*?:")
    _is_ready = False
    _conn = None

    def __init__(self, client_id, channel, server, port, debug=False):
        super(IRCConnector, self).__init__(client_id, channel, server, port, debug)
        self._client_id = client_id
        self._channel = channel
        self._server = server
        self._port = port
        self._debug = debug
        self._connect()
        self._start_queue_threads()

    def _connect(self):
        try:
            if self._conn:
                self._conn.close()
        finally:
            self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self._conn.connect((self._server, self._port))
        self._is_ready = False
        time.sleep(2)
        self._join()

    def _raw_send(self, text):
        if self._debug:
            print("<- " + text)
        self._conn.send(text + "\r\n")

    def _raw_recv(self):
        text = self._conn.recv(2 ** 14)
        if self._debug:
            print("-> " + text)
        return text

    def _join(self):
        self._raw_send("USER %s %s %s : " % (self._client_id, self._client_id, self._client_id))
        self._raw_send("NICK %s" % self._client_id)
        self._raw_send("JOIN %s" % self._channel)

    def _queue_recv(self):
        while True:
            try:
                lines = self._raw_recv()

                if not lines:
                    raise Exception("Connection terminated")

                for text in lines.splitlines():
                    if text.find('PING') != -1:
                        self._raw_send('PONG ' + text.split()[1])
                    elif "PRIVMSG" in text:
                        self._recv_queue.put(self._privmsg_re.sub("", text))
                    elif not self._is_ready:
                        self._is_ready = self._client_id in text and "JOIN" in text and self._channel in text
            except Exception as e:
                print(e)
                time.sleep(1)
                print("Reconnecting")

                try:
                    self._connect()
                except:
                    print("Could not reconnect, will try again.")

    def _dequeue_send(self):
        while not self._is_ready:
            time.sleep(1)

        while True:
            text = self._send_queue.get()

            try:
                self._raw_send("PRIVMSG %s %s" % (self._channel, text))
            except Exception as e:
                print(e)
                time.sleep(1)

                print("Requeuing message and reconnecting")
                self._send_queue.put(text)

                try:
                    self._connect()
                except:
                    print("Could not reconnect, will try again.")

    def is_ready(self):
        return self._is_ready

    def close(self):
        pass  # TODO