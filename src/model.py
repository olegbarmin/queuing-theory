import threading
from typing import Dict, List

from src.distribution import Distribution
from src.job.jobs import JobGenerator
from src.job.manager import ServerLoadManager
from src.job.server import ServerType
from src.stats.eventbus import EventBus
from src.systemtime import sleep, Stopwatch


class QueuingSystem:

    def __init__(self, input_interval_generator: Distribution, job_generator: JobGenerator,
                 simulation_duration, servers: Dict[ServerType, ServerLoadManager],
                 eventbus: EventBus) -> None:
        self._job_generator = job_generator
        self._interval_generator = input_interval_generator
        self._duration = simulation_duration
        self._server_managers = servers
        self._manager_threads = None
        self._servers_threads = None
        self._eventbus = eventbus

    def run(self):
        self._manager_threads = []
        self._servers_threads = []
        for t, m in list(self._server_managers.items()):
            thread = threading.Thread(target=m.run)
            self._manager_threads.append(thread)
            thread.start()
            for server in m.servers:
                thread = threading.Thread(target=server.run)
                self._servers_threads.append(thread)
                thread.start()

        self._start()

    def _start(self):
        stopwatch = Stopwatch()
        while not stopwatch.is_elapsed(self._duration):
            interval = int(self._interval_generator.next_random())
            sleep(interval)

            job = self._job_generator.next()
            self._eventbus.job_arrived(job)
            self._server_managers[ServerType.GATEWAY].schedule(job)

        self._stop()
        self._eventbus.all_jobs_processed()
        sleep(1000)  # since the printed lines order is not guaranteed, waiting some time for them to be flashed
        elapsed = stopwatch.elapsed()
        print("System: Simulation took {} ms".format(elapsed))

    def _stop(self):
        for t, m in list(self._server_managers.items()):
            m.stop()
        QueuingSystem._wait_for_thread_stop(self._manager_threads)
        for t, m in list(self._server_managers.items()):
            for s in m.servers:
                s.stop()
        QueuingSystem._wait_for_thread_stop(self._servers_threads)

    @staticmethod
    def _wait_for_thread_stop(threads: List[threading.Thread]):
        is_alive = True
        while is_alive:
            is_alive = all([t.is_alive() for t in threads])
            sleep(1)
