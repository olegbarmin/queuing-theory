import functools
import threading
from queue import PriorityQueue
from typing import Tuple, List

from src.job.jobs import Job
from src.systemtime import Stopwatch


class WaitTimeMetric:

    def __init__(self, job, wait_time) -> None:
        self._job = job
        self._wait_time = wait_time

    @property
    def wait_time(self):
        return self._wait_time


class JobStorage:

    def __init__(self, queue_size) -> None:
        self._queue = PriorityQueue(maxsize=queue_size)
        self._lock = threading.Lock()
        self._job_wait_dict = {}  # job ID: Stopwatch
        self._wait_metrics = []

    def add(self, job: Job) -> bool:
        with self._lock:
            return self._add(job)

    def pop(self) -> Tuple[Job, bool]:
        with self._lock:
            return self._pop()

    def is_empty(self) -> bool:
        with self._lock:
            return self._queue.empty()

    @property
    def stats(self) -> List[WaitTimeMetric]:
        return self._wait_metrics

    def _pop_stat(pop_func):
        @functools.wraps(pop_func)
        def decorator(self):
            job, success = pop_func(self)
            if success:
                job_id = job.id
                stopwatch = self._job_wait_dict.pop(job_id)
                wait_time = stopwatch.elapsed()
                metric = WaitTimeMetric(job, wait_time)
                self._wait_metrics.append(metric)
            return job, success

        return decorator

    @_pop_stat
    def _pop(self) -> Tuple[Job, bool]:
        result = (None, False)
        if not self._queue.empty():
            job = self._queue.get_nowait()
            result = (job, True)
        return result

    def _add_stat(add_func):
        @functools.wraps(add_func)
        def decorator(self, *args):
            job = args[0]
            success = add_func(self, job)
            if success:
                job_id = job.id
                self._job_wait_dict[job_id] = Stopwatch()
            return success

        return decorator

    @_add_stat
    def _add(self, job: Job) -> bool:
        job_queue_success = False
        if not self._queue.full():
            self._queue.put_nowait(job)
            job_queue_success = True
        return job_queue_success

    _add_stat = staticmethod(_add_stat)
    _pop_stat = staticmethod(_pop_stat)

    def size(self):
        return self._queue.qsize()
