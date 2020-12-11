import threading
from enum import Enum
from typing import Dict, Any

from src.distribution import Distribution
from src.job.jobs import Job, JobType
from src.stats.eventbus import EventBus
from src.systemtime import sleep


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
        self._log(f"Processing {job}... (ETA: {duration})")
        sleep(duration)
        self._eventbus.job_was_processed(job)

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
            # todo: stub must be removed
            super(GatewayServer, self)._process(job)
        else:
            self._log(f"{job} was sent to {server_type} servers")
            manager = self._managers[server_type]
            manager.schedule(job)
