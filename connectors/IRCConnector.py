from Queue import Queue

import re
import socket
import thread
import time

from AbstractConnector import AbstractConnector


class IRCConnector(AbstractConnector):
    _privmsg_re = re.compile(".*PRIVMSG.*?:")
    _is_ready = False
    _conn = None

    def __init__(self, client_id, channel, server, port, debug=False):
        self._send_queue = Queue()
        self._recv_queue = Queue()
        self._client_id = client_id
        self._channel = channel
        self._server = server
        self._port = int(port)
        self._debug = debug
        self._connect()

        # Start send and receive threads
        thread.start_new_thread(self._queue_recv, tuple())
        thread.start_new_thread(self._dequeue_send, tuple())

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
                        self._send_queue.put('PONG ' + text.split()[1])
                    elif "PRIVMSG" in text:
                        self._recv_queue.put(text)
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
            time.sleep(0.5)

        while True:
            text = self._send_queue.get()

            try:
                self._raw_send(text)
            except Exception as e:
                print(e)
                time.sleep(1)

                print("Requeuing message and reconnecting")
                self._send_queue.put(text)

                try:
                    self._connect()
                except:
                    print("Could not reconnect, will try again.")

    def send(self, text):
        self._send_queue.put("PRIVMSG %s %s" % (self._channel, text))

    def recv(self):
        return self._privmsg_re.sub("", self._recv_queue.get())

    def is_ready(self):
        return self._is_ready

    def close(self):
        pass  # TODO
