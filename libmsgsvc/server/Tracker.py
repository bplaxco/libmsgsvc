import os
import socket


class Tracker(object):
    """
    A tracker server to locate resources for channels
    """

    def __init__(self, srv_dir=".", port=5556):
        self._srv_dir = srv_dir
        self._servers_path = os.path.join(srv_dir, "servers.conf")
        self._channels_path = os.path.join(srv_dir, "channels.conf")
        self._server_index = 0
        self._port = port

        with open(self._servers_path) as servers:
            self._servers = servers.readlines()

        with open(self._channels_path) as channels:
            self._channels = {}

            for channel_conf in channels:
                channel, server = channel_conf.split()
                self._channels[channel] = server

    def cmd_REQSVR(self, channel):
        """
        handle a "REQSVR <channel>" request
        """
        server = self._channels.get(channel)

        if not server:
            server = self._servers[self._server_index % len(self._servers)]
            self._server_index = (self._server_index + 1) % len(self._servers)
            self._channels[channel] = server
            self.save()

        return server

    def save(self):
        with open(self._servers_path, "w") as servers:
            servers.write('\n'.join(self._servers))

        with open(self._channels_path, "w") as channels:
            channels.write('\n'.join([
                ' '.join(channel) for channel in self._channels.items()
            ]))

    def listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", self._port))
        sock.listen(1)

        while True:
            try:
                conn = sock.accept()[0]
                cmd_args = conn.recv(1024).split()
                conn.send(getattr(self, "cmd_%s" % cmd_args[0])(*cmd_args[1:]))
            except socket.error:
                pass
            finally:
                try:
                    conn.close()
                except:
                    pass
