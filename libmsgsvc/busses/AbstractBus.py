from Queue import Queue
import thread


class AbstractBus(object):
    def __init__(self):
        self._send_queue = Queue()
        self._recv_queue = Queue()

    def _start_queue_threads(self):
        thread.start_new_thread(self._queue_recv, tuple())
        thread.start_new_thread(self._dequeue_send, tuple())

    def send(self, obj):
        self._send_queue.put(obj)

    def recv(self, value=None):
        return self._recv_queue.get()

    def _queue_recv(self):
        raise NotImplementedError

    def _dequeue_send(self):
        raise NotImplementedError

    def is_ready(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError
