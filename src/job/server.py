import threading
from enum import Enum

from src.distribution import Distribution
from src.job.jobs import Job
from src.stats.eventbus import EventBus
from src.systemtime import sleep


class ServerTypes(Enum):
    GATEWAY = "Gateway"


class Server:

    def __init__(self, _type: ServerTypes, processing_distribution: Distribution, id_, eventbus: EventBus) -> None:
        self._type = _type
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
            if self._job is not None:
                raise Exception(f"Cannot start processing of {value} since is {self._job} is under processing")
            self._eventbus.job_process_start(value)
            self._job = value

    def run(self):
        self._log("Server was started...")
        while self._stop is not True:
            job = self._job
            if job is not None:
                self._process(job)
                self._job = None
            sleep(1)
        self._log("Server was stopped!")

    def stop(self):
        self._stop = True

    def _process(self, job: Job):
        duration = int(self._distribution.next_random())
        self._log("Processing {}...".format(job))
        sleep(duration)
        self._eventbus.job_was_processed(job)

    def _log(self, msg):
        print(f"Server {self._type.name} #{self._id}: {msg}")
