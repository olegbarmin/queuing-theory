import threading
from typing import List

from src.distribution import Distribution
from src.job.jobs import JobGenerator
from src.job.manager import ServerLoadManager
from src.job.server import JobProcessingServer
from src.systemtime import sleep, Stopwatch


class QueuingSystem:

    def __init__(self, input_interval_generator: Distribution, job_generator: JobGenerator,
                 simulation_duration, servers: List[JobProcessingServer], manager: ServerLoadManager) -> None:
        self._job_generator = job_generator
        self._interval_generator = input_interval_generator
        self._duration = simulation_duration
        self._servers = servers
        self._server_to_thread_dict = None
        self._manager = manager
        self._manager_thread = None

    def run(self):
        server_to_thread_dict = {server.id: threading.Thread(target=server.run) for server in self._servers}
        self._server_to_thread_dict = server_to_thread_dict

        self._manager_thread = threading.Thread(target=self._manager.run)
        self._manager_thread.start()

        for thread in list(server_to_thread_dict.values()):
            thread.start()
        self._start()

    def _start(self):
        stopwatch = Stopwatch()
        while not stopwatch.is_elapsed(self._duration):
            interval = int(self._interval_generator.next_random())
            sleep(interval)

            job = self._job_generator.next()
            self._manager.process(job)

        self._stop()
        elapsed = stopwatch.elapsed()
        print("System: Simulation took {} ms".format(elapsed))

    def _stop(self):
        self._manager.stop()
        QueuingSystem._wait_for_thread_stop(self._manager_thread)
        self._stop_servers()
        sleep(1000)  # since the printed lines order is not guaranteed, waiting some time for them to be flashed

    def _stop_servers(self):
        for server in self._servers:
            server.stop()
            self._wait_server_stop(server)

    def _wait_server_stop(self, server: JobProcessingServer):
        thread = self._server_to_thread_dict[server.id]
        QueuingSystem._wait_for_thread_stop(thread)

        print("System: Server {} finished execution".format(server.id))

    @staticmethod
    def _wait_for_thread_stop(thread: threading.Thread):
        while thread.is_alive():
            sleep(1)
