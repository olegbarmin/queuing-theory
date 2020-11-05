from typing import List


class JobProcessTimeMetric:

    def __init__(self, job, process_time) -> None:
        self._job = job
        self._process_time = process_time

    @property
    def process_time(self):
        return self._process_time


class LoadMetric:
    def __init__(self) -> None:
        self._jobs_number = []

    def add(self, queue_size: int):
        self._jobs_number.append(queue_size)

    @property
    def load_values(self):
        return self._jobs_number

    def average_load(self) -> int:
        return sum(self._jobs_number) / len(self._jobs_number) if len(self._jobs_number) is not 0 else 0


class QueueSizeMetric:

    def __init__(self) -> None:
        self._sizes = []

    def add(self, queue_size: int):
        self._sizes.append(queue_size)

    @property
    def queue_sizes(self) -> List[int]:
        return self._sizes

    def average_queue_size(self) -> int:
        return sum(self._sizes) / len(self._sizes) if len(self._sizes) is not 0 else 0
