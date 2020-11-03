import threading

from src.distribution import Distribution
from src.job.jobs import Job
from src.job.queue import JobsQueue
from src.systemtime import sleep, Stopwatch


class JobProcessingServer:

    def __init__(self, processing_distribution: Distribution, queue: JobsQueue, id_: int = 1) -> None:
        self._distribution = processing_distribution
        self._queue = queue
        self._stop = False
        self._id = id_

    def stop(self):
        self._stop = True

    def start(self):
        thread = threading.Thread(target=self._start)
        thread.start()

    def _start(self):
        self._log("Execution started!")
        while self._stop is not True:
            job, has_job = self._queue.pop()
            if has_job:
                self._log("Processing {} job".format(job))
                self._process(job)
        self._log("Execution finished!")

    def _process(self, job: Job):
        duration = int(self._distribution.next_random())
        stopwatch = Stopwatch()
        while not stopwatch.is_elapsed(duration):
            sleep(1)
        self._log("Job '{}' was processed for {}".format(job, stopwatch.elapsed()))

    def _log(self, msg):
        print("Server {}: {}".format(self._id, msg))
