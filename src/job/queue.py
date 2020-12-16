import collections
import threading
from typing import Tuple

from src.job.jobs import Job


class JobStorage:

    def __init__(self, queue_size) -> None:
        self._queue = collections.deque(maxlen=queue_size)
        self._lock = threading.Lock()

    def add(self, job: Job) -> bool:
        with self._lock:
            return self._add(job)

    def pop(self) -> Tuple[Job, bool]:
        with self._lock:
            return self._pop()

    def is_empty(self) -> bool:
        with self._lock:
            return not self._queue

    def _pop(self) -> Tuple[Job, bool]:
        result = (None, False)
        if self._queue:
            job = self._queue.pop()
            result = (job, True)
        return result

    def _add(self, job: Job) -> bool:
        success = False
        if len(self._queue) < self._queue.maxlen:
            self._queue.append(job)
            success = True
        return success

    def size(self):
        return len(self._queue)

    def __str__(self) -> str:
        return f"[{len(self._queue)}/{self._queue.maxlen}]"
