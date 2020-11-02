from src.distribution import Distribution
from src.job.jobs import JobGenerator
from src.systemtime import sleep, Stopwatch


class QueuingSystem:

    def __init__(self, input_interval_generator: Distribution, job_generator: JobGenerator,
                 simulation_duration) -> None:
        self._job_generator = job_generator
        self._interval_generator = input_interval_generator
        self._duration = simulation_duration

    def start(self):
        stopwatch = Stopwatch()
        while not stopwatch.is_elapsed(self._duration):
            interval = int(self._interval_generator.next_random())
            sleep(interval)

            job = self._job_generator.next()
            self._process_job(job)

        print("Simulation took {} ms".format(stopwatch.elapsed()))

    def _process_job(self, job):
        print(job)
