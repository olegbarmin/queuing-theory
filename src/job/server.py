import functools
import threading
from typing import List

from src.distribution import Distribution
from src.job.jobs import Job
from src.job.queue import JobStorage
from src.systemtime import sleep, Stopwatch


class JobProcessTimeMetric:

    def __init__(self, job, process_time) -> None:
        self._job = job
        self._process_time = process_time

    @property
    def process_time(self):
        return self._process_time


class JobProcessingServer:

    def __init__(self, processing_distribution: Distribution, queue: JobStorage, id_: int = 1) -> None:
        self._distribution = processing_distribution
        self._queue = queue
        self._stop = False
        self._id = id_
        self._job_metrics = []

    @property
    def id(self):
        return self._id

    def start(self):
        thread = threading.Thread(target=self._start)
        thread.start()

    def stop(self):
        self._stop = True

    @property
    def stats(self) -> List[JobProcessTimeMetric]:
        return self._job_metrics

    def _start(self):
        self._log("Execution started!")
        while self._stop is not True:
            job, has_job = self._queue.pop()
            if has_job:
                self._process(job)
        self._log("Execution finished!")

    def _process_stat(func):
        @functools.wraps(func)
        def decorator(self, *args):
            job = args[0]

            stopwatch = Stopwatch()
            func(self, job)
            process_time = stopwatch.elapsed()
            self._job_metrics.append(JobProcessTimeMetric(job.id, process_time))

        return decorator

    @_process_stat
    def _process(self, job: Job):
        duration = int(self._distribution.next_random())
        self._log("Processing {} job".format(job))
        stopwatch = Stopwatch()
        while not stopwatch.is_elapsed(duration):
            sleep(1)
        self._log("Job '{}' was processed for {}".format(job, stopwatch.elapsed()))

    def _log(self, msg):
        print("Server {}: {}".format(self._id, msg))

    _process_stat = staticmethod(_process_stat)
