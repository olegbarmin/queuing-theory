import threading
from enum import Enum
from typing import Dict, Any

from src.distribution import Distribution
from src.job.jobs import Job, JobType
from src.stats.eventbus import EventBus
from src.systemtime import sleep, Stopwatch


class ServerType(Enum):
    GATEWAY = "Gateway"
    INVENTORY = "Inventory"
    SHIPMENT = "Shipment"
    PAYMENTS = "Payments"


class Server:

    def __init__(self, _type: ServerType, processing_distribution: Distribution, id_, eventbus: EventBus) -> None:
        self._type = _type
        self._distribution = processing_distribution
        self._stop = False
        self._job = None
        self._id = id_
        self._lock = threading.Lock()
        self._eventbus = eventbus
        self._stopped = True

    @property
    def id(self):
        return self._id

    @property
    def type(self):
        return self._type

    def is_idle(self) -> bool:
        return self._job is None

    @property
    def job(self):
        return self._job

    @property
    def stopped(self):
        return self._stopped

    @job.setter
    def job(self, value: Job):
        with self._lock:
            if self._job is not None:
                raise Exception(f"Cannot start processing of {value} since is {self._job} is under processing")
            if self._stop:
                raise Exception(f"Server {self._type} #{self._id} was stooped, job cannot be assigned")
            self._eventbus.job_process_start(self.type, value)
            self._job = value

    def run(self):
        self._log("Server was started...")
        self._stopped = False
        while self._stop is not True:
            job = self._job
            if job is not None:
                self._process(job)
                self._job = None
            sleep(1)
        self._stopped = True
        self._log("Server was stopped!")

    def stop(self):
        self._stop = True

    def _process(self, job: Job):
        duration = int(self._distribution.next_random())
        self._log(f"Processing {job}... (ETA: {duration})")
        stopwatch = Stopwatch()
        sleep(duration)

        self._eventbus.job_was_processed(self.type, job)
        self._log(f"{job} was processed for {stopwatch.elapsed()} ms")

    def _log(self, msg):
        print(f"Server {self._type.name} #{self._id}: {msg}")


JOB_TO_SERVER_TYPE = {
    JobType.SHOW_PRODUCTS: ServerType.INVENTORY,
    JobType.CHECKOUT: ServerType.SHIPMENT,
    JobType.PAYMENT: ServerType.PAYMENTS
}


class GatewayServer(Server):

    def __init__(self, _type: ServerType, processing_distribution: Distribution, id_, eventbus: EventBus,
                 managers: Dict[ServerType, Any]) -> None:
        super().__init__(_type, processing_distribution, id_, eventbus)
        self._managers = {k: v for k, v in managers.items() if k != ServerType.GATEWAY}

    def _process(self, job: Job):
        server_type = JOB_TO_SERVER_TYPE[job.type]
        if server_type not in self._managers:
            self._log(f"{server_type} server was not found to process {job}")
            raise Exception(f"Server for {job} wasn't found")
        else:
            self._log(f"{job} was passed to {server_type} servers")
            manager = self._managers[server_type]
            manager.schedule(job)
            random = int(self._distribution.next_random())
            sleep(random)
            self._eventbus.job_was_passed(self.type, job)
