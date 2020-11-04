import threading
from typing import List

from src.job.jobs import Job
from src.job.queue import JobStorage
from src.job.server import JobProcessingServer
from src.systemtime import sleep


class ServerLoadManager:

    def __init__(self, servers: List[JobProcessingServer], queue: JobStorage) -> None:
        self._servers_dict = {server.id: server for server in servers}
        self._queue = queue
        self._lock = threading.Lock()
        self._stop = False

    def start(self):
        thread = threading.Thread(target=self._load_servers)
        thread.start()

    def stop(self):
        self._stop = True

    def _load_servers(self):
        while self._stop is not True:
            self._try_pick_job_from_queue()
            sleep(1)

    def _try_pick_job_from_queue(self):
        for server in list(self._servers_dict.values()):
            with self._lock:
                if server.is_idle():
                    job, exist = self._queue.pop()
                    if exist:
                        print("Manager: Picking job {} from queue to {} server".format(job.id, server.id))
                        server.job = job

    def process(self, job: Job):
        with self._lock:
            if not self._queue.is_empty():
                self._queue_job(job)
            else:
                found_idle_server = False
                for server in list(self._servers_dict.values()):
                    if server.is_idle():
                        print("Manager: Processing job {} directly by {} server".format(job.id, server.id))
                        server.job = job
                        found_idle_server = True
                        break

                if not found_idle_server:
                    self._queue_job(job)

    def _queue_job(self, job: Job):
        success = self._queue.add(job)
        if not success:
            print(
                "Manager: Job {} was dropped since queue is full (queue size = {})".format(job.id, self._queue.size()))
        else:
            print("Manager: Job {} was queued (queue size = {})".format(job.id, self._queue.size()))
