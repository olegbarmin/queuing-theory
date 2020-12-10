from threading import Thread


class Runnable:

    def __init__(self) -> None:
        self._thread = None

    @property
    def thread(self):
        return self._thread

    @thread.setter
    def thread(self, value: Thread):
        self._thread = value
