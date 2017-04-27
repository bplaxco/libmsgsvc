class AbstractConnector(object):
    """
    Every connector should implement these methods.
    """

    def __init__(self, client_id, channel, server, port, debug=False):
        raise NotImplementedError

    def send(self, text):
        raise NotImplementedError

    def recv(self):
        raise NotImplementedError

    def is_ready(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError
