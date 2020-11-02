import time

from src.distribution import Distribution


class QueuingSystem:

    def __init__(self, input_interval_generator: Distribution, job_generator, simulation_duration) -> None:
        self._job_generator = job_generator
        self._interval_generator = input_interval_generator
        self._duration = simulation_duration

    def start(self):
        interval = int(self._interval_generator.next_random())
        print(interval)
        _sleep(interval)


def _sleep(millis: int):
    if not isinstance(millis, int):
        raise Exception("Int value expected as sleep argument. Actual: {} ({})".format(millis, type(millis)))
    time.sleep(millis / 1000)


def _current_millis() -> int:
    return int(round(time.time() * 1000))
