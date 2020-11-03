import threading
from typing import List

from src.distribution import Distribution
from src.job.jobs import JobGenerator
from src.job.queue import JobStorage
from src.job.server import JobProcessingServer
from src.systemtime import sleep, Stopwatch


class QueuingSystem:

    def __init__(self, input_interval_generator: Distribution, job_generator: JobGenerator,
                 simulation_duration, servers: List[JobProcessingServer], queue: JobStorage) -> None:
        self._job_generator = job_generator
        self._interval_generator = input_interval_generator
        self._duration = simulation_duration
        self._servers = servers
        self._queue = queue

    def start(self):
        system_thread = threading.Thread(target=self._start)
        server_threads = [threading.Thread(target=server.start) for server in self._servers]

        system_thread.start()
        for thread in server_threads:
            thread.start()

    def _start(self, ):
        stopwatch = Stopwatch()
        while not stopwatch.is_elapsed(self._duration):
            interval = int(self._interval_generator.next_random())
            sleep(interval)

            job = self._job_generator.next()
            self._process_job(job)

        self._stop_servers()
        print("System: Simulation took {} ms".format(stopwatch.elapsed()))

    def _process_job(self, job):
        success = self._queue.add(job)
        if not success:
            print("System: Jobs queue is full!")

    def _stop_servers(self):
        for server in self._servers:
            server.stop()
