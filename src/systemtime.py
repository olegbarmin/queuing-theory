import time


def sleep(millis: int):
    if not isinstance(millis, int):
        raise Exception("Int value expected as sleep argument. Actual: {} ({})".format(millis, type(millis)))
    time.sleep(millis / 1000)


def current_millis() -> int:
    return int(round(time.time() * 1000))


class Stopwatch:
    def __init__(self) -> None:
        self._start = current_millis()

    def elapsed(self) -> int:
        return current_millis() - self._start

    def is_elapsed(self, duration) -> bool:
        elapsed = self.elapsed()
        return elapsed > duration
