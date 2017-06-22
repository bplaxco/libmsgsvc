import re
import socket
import thread
import time


class IRCConnector(object):
    _conn = None
    _is_closed = False
    _is_ready = False
    _privmsg_re = re.compile(".*PRIVMSG.*?:")
    _subscriber_count = 0

    def __init__(self, client, debug=False):
        self._client = client
        self._debug = debug
        self._connect()
        thread.start_new_thread(self._recv, ())

        while not self._is_ready:
            time.sleep(1)

    def _connect(self):
        if self._is_closed:
            return

        try:
            if self._conn:
                self._conn.close()
        except:
            pass
        finally:
            self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self._conn.connect(self._client.get_server_and_port())
        self._is_ready = False
        time.sleep(2)
        client_id = self._client.get_id()
        channel = self._client.get_channel()
        self._raw_send("USER %s %s %s : " % (client_id, client_id, client_id))
        self._raw_send("NICK %s" % client_id)
        self._raw_send("JOIN %s" % channel)

    def _raw_send(self, text):
        if self._is_closed:
            return
        if self._debug:
            print("<- " + text)
        self._conn.send(text + "\r\n")

    def _raw_recv(self):
        if self._is_closed:
            return ""
        text = self._conn.recv(2 ** 14)
        if self._debug:
            print("-> " + text)
        return text

    def _recv(self):
        while not self._is_closed:
            client_id = self._client.get_id()
            channel = self._client.get_channel()
            try:
                lines = self._raw_recv()
                if not lines:
                    raise Exception("Connection terminated")
                for text in lines.splitlines():
                    if "PRIVMSG" in text:
                        self._client.recv(self._privmsg_re.sub("", text))
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
                if self._is_closed:
                    return
                print(e)
                time.sleep(1)
                print("Reconnecting")
                try:
                    self._connect()
                except:
                    print("Could not reconnect, will try again.")

    def send(self, text):
        while not self._is_ready:
            time.sleep(1)
        while not self._is_closed:
            try:
                return self._raw_send("PRIVMSG %s %s" % (
                    self._client.get_channel(), text,
                ))
            except Exception as e:
                if self._is_closed:
                    return
                print(e)
                time.sleep(1)
                print("Starting another attempt...")
                try:
                    self._connect()
                except:
                    print("Could not reconnect, will try again.")

    def get_subscriber_count(self):
        return self._subscriber_count

    def close(self):
        self._is_closed = True
        self._raw_send("QUIT")
