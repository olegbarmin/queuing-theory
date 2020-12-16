from typing import List

from src.systemtime import Stopwatch


class JobProcessTimeMetric:

    def __init__(self, job, process_time) -> None:
        self._job = job
        self._process_time = process_time

    @property
    def process_time(self):
        return self._process_time


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


class WaitTimeMetric:

    def __init__(self, job, wait_time) -> None:
        self._job = job
        self._wait_time = wait_time

    @property
    def wait_time(self):
        return self._wait_time


IDLE = "IDLE"
BUSY = "BUSY"


class LoadMetric:

    def __init__(self) -> None:
        self._jobs_number = 0
        self._state_changes = []
        self._stopwatch = Stopwatch()
        print("SimulationStatistics: start state stopwatch")
        self._current_state = IDLE

    def job_in(self):
        self._jobs_number += 1
        self._record_busy()

    def job_out(self):
        self._jobs_number -= 1
        if self._jobs_number < 0:
            raise Exception("Number of processed out jobs exceeded number arrived jobs")
        if self._jobs_number == 0:
            self._record_idle()

    def _record_idle(self):
        if self._current_state is BUSY:
            elapsed = self._stopwatch.elapsed()
            self._state_changes.append((self._current_state, elapsed))
            self._current_state = IDLE
            self._stopwatch = Stopwatch()
            print("SimulationStatistics: System is IDLE (BUSY for {} ms)".format(elapsed))

    def _record_busy(self):
        if self._current_state is IDLE:
            elapsed = self._stopwatch.elapsed()
            self._state_changes.append((self._current_state, elapsed))
            self._current_state = BUSY
            self._stopwatch = Stopwatch()
            print("SimulationStatistics: System is BUSY (IDLE for {} ms)".format(elapsed))

    def stop_record(self):
        elapsed = self._stopwatch.elapsed()
        state = self._current_state
        print("SimulationStatistics: Final state is {} for {}".format(state, elapsed))
        self._state_changes.append((state, elapsed))
        self._current_state = None
        self._stopwatch = None
        if self._jobs_number != 0:
            raise Exception(f"Jobs number in the system after simulation: {self._jobs_number}")

    def idle_time(self):
        idle_states = filter(lambda state_change: state_change[0] is IDLE, self._state_changes)
        return sum(map(lambda x: x[1], idle_states))

    def busy_time(self):
        busy_states = filter(lambda state_change: state_change[0] is BUSY, self._state_changes)
        return sum(map(lambda x: x[1], busy_states))

    def total_time(self):
        busy_time = self.busy_time()
        idle_time = self.idle_time()
        return busy_time + idle_time

    def idle_probability(self) -> float:
        busy_time = self.busy_time()
        idle_time = self.idle_time()
        total_time = busy_time + idle_time
        return round((idle_time / total_time) * 100, 2)

    def is_busy(self):
        return self._current_state == BUSY


class JobDropMetric:
    def __init__(self) -> None:
        self._total_jobs = 0
        self._processed_jobs = 0
        self._dropped_jobs = 0

    def record_job_arrival(self):
        self._total_jobs = self._total_jobs + 1

    def record_job_processed(self):
        self._processed_jobs = self._processed_jobs + 1

    def record_job_drop(self):
        self._dropped_jobs = self._dropped_jobs + 1

    def job_drop_chance(self):
        return round(float(self._dropped_jobs) / float(self._total_jobs) * 100, 2)
