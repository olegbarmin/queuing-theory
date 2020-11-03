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
        self._server_to_thread_dict = None

    def start(self):
        server_to_thread_dict = {server.id: threading.Thread(target=server.start) for server in self._servers}
        self._server_to_thread_dict = server_to_thread_dict

        for thread in list(server_to_thread_dict.values()):
            thread.start()
        self._start()

    def _start(self, ):
        stopwatch = Stopwatch()
        while not stopwatch.is_elapsed(self._duration):
            interval = int(self._interval_generator.next_random())
            sleep(interval)

            job = self._job_generator.next()
            self._process_job(job)

        self._stop_servers()
        elapsed = stopwatch.elapsed()
        sleep(500)  # since the printed lines order is not guaranteed, waiting some time for them to be flashed
        print("System: Simulation took {} ms".format(elapsed))

    def _process_job(self, job):
        success = self._queue.add(job)
        if not success:
            print("System: Jobs queue is full!")

    def _stop_servers(self):
        for server in self._servers:
            server.stop()
            self._wait_server_stop(server)

    def _wait_server_stop(self, server: JobProcessingServer):
        thread = self._server_to_thread_dict[server.id]
        while thread.is_alive():
            sleep(1)  # interval between retries whether sever was stopped

        print("System: Server {} finished execution".format(server.id))
