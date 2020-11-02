import time

from src.distribution import Distribution
from src.jobs import JobGenerator


class QueuingSystem:

    def __init__(self, input_interval_generator: Distribution, job_generator: JobGenerator,
                 simulation_duration) -> None:
        self._job_generator = job_generator
        self._interval_generator = input_interval_generator
        self._duration = simulation_duration

    def start(self):
        start_time = _current_millis()
        current_time = _current_millis()
        elapsed = current_time - start_time
        while self._duration > elapsed:
            interval = int(self._interval_generator.next_random())
            _sleep(interval)

            job = self._job_generator.next()
            print(job)

            current_time = _current_millis()
            elapsed = current_time - start_time

        print("Simulation took {} ms".format(elapsed))


def _sleep(millis: int):
    if not isinstance(millis, int):
        raise Exception("Int value expected as sleep argument. Actual: {} ({})".format(millis, type(millis)))
    time.sleep(millis / 1000)


def _current_millis() -> int:
    return int(round(time.time() * 1000))
