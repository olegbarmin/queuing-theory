import threading

from src.distribution import Distribution
from src.job.jobs import Job
from src.stats.eventbus import EventBus
from src.systemtime import sleep, Stopwatch


class JobProcessingServer:

    def __init__(self, processing_distribution: Distribution, id_, eventbus: EventBus) -> None:
        self._distribution = processing_distribution
        self._stop = False
        self._job = None
        self._id = id_
        self._lock = threading.Lock()
        self._eventbus = eventbus

    @property
    def id(self):
        return self._id

    def is_idle(self) -> bool:
        return self._job is None

    @property
    def job(self):
        return self._job

    @job.setter
    def job(self, value: Job):
        with self._lock:
            self._eventbus.job_process_start(value)
            self._job = value

    def run(self):
        self._log("Server was started...")
        while self._stop is not True:
            job = self._job
            if job is not None:
                if self._process(job):
                    self._job = None
            sleep(1)
        self._log("Server was stopped!")

    def stop(self):
        self._stop = True

    def _process(self, job: Job) -> bool:
        duration = int(self._distribution.next_random())
        self._log("Processing {}...".format(job))
        stopwatch = Stopwatch()
        finished = True
        while not stopwatch.is_elapsed(duration):
            sleep(1)
            if self._job.id is not job.id:
                finished = False
                break
        if finished:
            self._log("Job '{}' was processed for {}".format(job.id, stopwatch.elapsed()))
            self._eventbus.job_was_processed(job)
        else:
            self._log("Processing of {} was aborted to start processing of {} with higher priority"
                      .format(job, self.job))
        return finished

    def _log(self, msg):
        print("Server {}: {}".format(self._id, msg))
