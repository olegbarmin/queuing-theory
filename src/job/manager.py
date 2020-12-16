import threading
from typing import List

from src.job.jobs import Job
from src.job.queue import JobStorage
from src.job.server import Server
from src.stats.eventbus import EventBus
from src.systemtime import sleep
from src.thread import Runnable


class ServerLoadManager(Runnable):

    def __init__(self, servers: List[Server], queue_size: int, eventbus: EventBus) -> None:
        super().__init__()
        self._servers_dict = {server.id: server for server in servers}
        self._type = servers[0].type
        self._queue = JobStorage(queue_size)
        self._lock = threading.Lock()
        self._stop = False
        self._stopped = True
        self._eventbus = eventbus

    @property
    def servers(self):
        return list(self._servers_dict.values())

    @property
    def queue(self):
        return self._queue

    @property
    def stopped(self):
        return self._stopped

    def run(self):
        self._stopped = False
        # runs until stop command received and queue is cleared
        while not self._stop or (self._stop and not self._queue.is_empty()):
            self._try_pick_job_from_queue()
            sleep(1)
        self._stopped = True
        self.log("Queue is empty, queue clearing thread stopped.")

    def stop(self):
        self._stop = True

    def _try_pick_job_from_queue(self):
        with self._lock:
            for server in list(self._servers_dict.values()):
                if server.is_idle():
                    job, exist = self._queue.pop()
                    if exist:
                        self.log("Picking job {} from queue to #{} server (queue size = {})"
                                 .format(job, server.id, self._queue.size()))
                        self._eventbus.job_pop_from_queue(self._type, job)
                        server.job = job

    def schedule(self, job: Job) -> bool:
        with self._lock:
            scheduled = self._assign_server(job)
            if not scheduled:
                scheduled = self._queue_job(job)
            if scheduled:
                self._eventbus.job_schedule(self._type, job)

            return scheduled

    def _queue_job(self, job: Job) -> bool:
        success = self._queue.add(job)
        if success:
            self.log(f"{job} was queued {self._queue}")
            self._eventbus.job_queued(self._type, job)
        else:
            self.log(f"Job {job} was dropped since queue is full {self._queue}")
            self._eventbus.job_rejected(self._type, job)

        return success

    def _assign_server(self, job: Job):
        found_server = False
        for server in list(self._servers_dict.values()):
            if server.is_idle():
                self.log("Processing job {} directly by {} server".format(job.id, server.id))
                server.job = job
                found_server = True
                break

        return found_server

    def log(self, msg):
        print(f"Manager ({self._type.name}): {msg}")
