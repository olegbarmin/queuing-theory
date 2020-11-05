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

    def run(self):
        # runs until stop command received and queue is cleared
        while self._stop is not True or (self._stop is True and not self._queue.is_empty()):
            self._try_pick_job_from_queue()
            sleep(1)
        print("Manager: Queue is empty, queue clearing thread stopped.")

    def stop(self):
        self._stop = True

    def _try_pick_job_from_queue(self):
        for server in list(self._servers_dict.values()):
            with self._lock:
                if server.is_idle():
                    job, exist = self._queue.pop()
                    if exist:
                        print("Manager: Picking job {} from queue to {} server (queue size = {})"
                              .format(job.id, server.id, self._queue.size()))
                        server.job = job

    def process(self, job: Job):
        with self._lock:
            if not self._assign_server(job):
                self._queue_job(job)

    def _queue_job(self, job: Job):
        dropped, success = self._queue.add(job)
        if not success:
            print("Manager: Job {} was dropped since queue is full (queue size = {})"
                  .format(job.id, self._queue.size()))
        elif success and dropped is not None:
            print("Manager: {} was removed from queue since the {} has higher priority (queue size = {})"
                  .format(dropped, job, self._queue.size()))
        else:
            print("Manager: {} was queued (queue size = {})".format(job, self._queue.size()))

    def _assign_server(self, job: Job):
        found_server = False
        for server in list(self._servers_dict.values()):
            if server.is_idle():
                print("Manager: Processing job {} directly by {} server".format(job.id, server.id))
                server.job = job
                found_server = True
                break

        if not found_server:  # idle server wasn't found, looking for a server which processing lower priority job
            for server in list(self._servers_dict.values()):
                if server.job.priority > job.priority:
                    # print("Manager: Server {} processing lower priority {} hence switching it to {}"
                    #       .format(server.id, server.job, job))
                    server.job = job
                    found_server = True

        return found_server
