class AbstractConnector(object):
    """
    This is the abstract class for a connector. Every connector should implement
    these methods
    """

    def __init__(self, client_id, channel, server, port, debug=False):
        pass

    def send(self, text):
        raise NotImplementedError

    def recv(self):
        raise NotImplementedError

    def is_ready(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError
