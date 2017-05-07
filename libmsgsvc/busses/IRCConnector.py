import re
import socket
import time

from AbstractBus import AbstractBus


class IRCConnector(AbstractBus):
    _privmsg_re = re.compile(".*PRIVMSG.*?:")
    _is_ready = False
    _conn = None
    _subscriber_count = 0
    _do_reconnect = True

    def __init__(self, connection_info, debug=False):
        super(IRCConnector, self).__init__()
        self._connection_info = connection_info
        self._debug = debug
        self._connect()
        self._start_queue_threads()

    def _connect(self):
        if self.is_closed():
            return

        try:
            if self._conn:
                self._conn.close()
        finally:
            self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self._conn.connect(self._connection_info.get_server_and_port())
        self._is_ready = False
        time.sleep(2)
        self._join()

    def _raw_send(self, text):
        if self.is_closed():
            return

        if self._debug:
            print("<- " + text)
        self._conn.send(text + "\r\n")

    def _raw_recv(self):
        if self.is_closed():
            return ""

        text = self._conn.recv(2 ** 14)
        if self._debug:
            print("-> " + text)
        return text

    def _join(self):
        client_id = self._connection_info.get_client_id()
        channel = self._connection_info.get_channel()

        self._raw_send("USER %s %s %s : " % (client_id, client_id, client_id))
        self._raw_send("NICK %s" % client_id)
        self._raw_send("JOIN %s" % channel)

    def _queue_recv(self):
        while self._do_reconnect:
            client_id = self._connection_info.get_client_id()
            channel = self._connection_info.get_channel()

            try:
                lines = self._raw_recv()

                if not lines:
                    raise Exception("Connection terminated")

                for text in lines.splitlines():
                    if "PRIVMSG" in text:
                        self._recv_queue.put(self._privmsg_re.sub("", text))

                    # Handle server ping
                    elif text.find('PING') != -1:
                        self._raw_send('PONG ' + text.split()[1])

                    # Set ready status on JOIN
                    elif not self._is_ready:
                        self._is_ready = (
                            client_id in text and
                            channel in text and
                            "JOIN" in text
                        )

                    # Update subscriber count
                    elif "353 " + client_id in text and channel in text:
                        self._subscriber_count = len(text.split(":")[2].split()) - 1

                    # Send NAMES query on join and quit
                    elif "JOIN " + channel in text or "QUIT" in text:
                        self._raw_send("NAMES " + channel)

            except Exception as e:
                if self.is_closed():
                    return

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

        while self._do_reconnect:
            text = self._send_queue.get()

            try:
                self._raw_send("PRIVMSG %s %s" % (
                    self._connection_info.get_channel(), text,
                ))
            except Exception as e:
                if self.is_closed():
                    return

                print(e)
                time.sleep(1)

                print("Requeuing message and reconnecting")
                self._send_queue.put(text)

                try:
                    self._connect()
                except:
                    print("Could not reconnect, will try again.")

    def get_subscriber_count(self):
        return self._subscriber_count

    def is_ready(self):
        return self._is_ready

    def is_closed(self):
        return not self._do_reconnect

    def close(self):
        self._do_reconnect = False
        self._raw_send("QUIT")
