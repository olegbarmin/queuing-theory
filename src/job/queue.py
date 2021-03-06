import heapq
import threading
from typing import Tuple

from src.job.jobs import Job


class PriorityQueue:

    def __init__(self, maxsize) -> None:
        self._maxsize = maxsize
        self._data = []

    def put(self, job: Job) -> Tuple[Job, bool]:
        """
        When queue reaches max len, might replace job with lower priority with
        job with higher one.
        Returns tuple of Job and bool. Job is None when no job was dropped from queue.
        """
        success = False
        dropped_job = None
        if len(self._data) < self._maxsize:
            heapq.heappush(self._data, job)
            success = True
        elif max(self._data).priority > job.priority:
            lowest_priority = max(self._data)
            self._data.remove(lowest_priority)
            dropped_job = lowest_priority
            heapq.heapify(self._data)
            heapq.heappush(self._data, job)
            success = True
        return dropped_job, success

    def pop(self):
        return heapq.heappop(self._data)

    def full(self):
        return len(self._data) is self._maxsize

    def empty(self):
        return len(self._data) is 0

    def size(self):
        return len(self._data)


class JobStorage:

    def __init__(self, queue_size) -> None:
        self._queue = PriorityQueue(maxsize=queue_size)
        self._lock = threading.Lock()

    def add(self, job: Job) -> Tuple[Job, bool]:
        with self._lock:
            return self._add(job)

    def pop(self) -> Tuple[Job, bool]:
        with self._lock:
            return self._pop()

    def is_empty(self) -> bool:
        with self._lock:
            return self._queue.empty()

    def _pop(self) -> Tuple[Job, bool]:
        result = (None, False)
        if not self._queue.empty():
            job = self._queue.pop()
            result = (job, True)
        return result

    def _add(self, job: Job) -> Tuple[Job, bool]:
        return self._queue.put(job)

    def size(self):
        return self._queue.size()
