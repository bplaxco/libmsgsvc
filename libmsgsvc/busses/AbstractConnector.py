from AbstractBus import AbstractBus


class AbstractConnector(AbstractBus):
    """
    Every connector should implement these methods.
    """

    def __init__(self, client_id, channel, server, port, debug=False):
        super(AbstractConnector, self).__init__()

    def _queue_recv(self):
        raise NotImplementedError

    def _dequeue_send(self):
        raise NotImplementedError

    def is_ready(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError