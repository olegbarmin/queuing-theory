import functools
import threading
from typing import List

from src.distribution import Distribution
from src.job.jobs import Job
from src.systemtime import sleep, Stopwatch


class JobProcessTimeMetric:

    def __init__(self, job, process_time) -> None:
        self._job = job
        self._process_time = process_time

    @property
    def process_time(self):
        return self._process_time


class JobProcessingServer:

    def __init__(self, processing_distribution: Distribution, id_) -> None:
        self._distribution = processing_distribution
        self._stop = False
        self._job = None
        self._id = id_
        self._job_metrics = []
        self._lock = threading.Lock()

    @property
    def id(self):
        return self._id

    def is_idle(self) -> bool:
        return self._job is None

    @property
    def job(self):
        with self._lock:
            return self._job

    @job.setter
    def job(self, value: Job):
        with self._lock:
            if self._job is not None:
                raise Exception("Job {} is already assigned to {} server. It cannot be changed to {} job"
                                .format(self._job.id, self.id, value.id))
            self._job = value

    def run(self):
        self._log("Server was started...")
        while self._stop is not True:
            job = self._job
            if job is not None:
                self._process(job)
                self._job = None
        self._log("Server was stopped!")

    def stop(self):
        self._stop = True

    @property
    def stats(self) -> List[JobProcessTimeMetric]:
        return self._job_metrics

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
        self._log("Processing job {}...".format(job.id))
        stopwatch = Stopwatch()
        while not stopwatch.is_elapsed(duration):
            sleep(1)
        self._log("Job '{}' was processed for {}".format(job.id, stopwatch.elapsed()))

    def _log(self, msg):
        print("Server {}: {}".format(self._id, msg))

    _process_stat = staticmethod(_process_stat)
