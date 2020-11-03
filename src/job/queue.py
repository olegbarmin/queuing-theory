import threading
from queue import Queue
from typing import Tuple

from src.job.jobs import Job


class JobStorage:

    def __init__(self, queue_size) -> None:
        self._queue = Queue(queue_size)
        self._lock = threading.Lock()

    def add(self, job: Job) -> bool:
        with self._lock:
            return self._add(job)

    def pop(self) -> Tuple[Job, bool]:
        with self._lock:
            return self._pop()

    def _add(self, job: Job) -> bool:
        job_queue_success = False
        if not self._queue.full():
            self._queue.put_nowait(job)
            job_queue_success = True
        return job_queue_success

    def _pop(self) -> Tuple[Job, bool]:
        result = (None, False)
        if not self._queue.empty():
            job = self._queue.get_nowait()
            result = (job, True)
        return result
