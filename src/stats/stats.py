from typing import List

from tabulate import tabulate

from src.job.jobs import Job
from src.job.queue import JobStorage
from src.job.server import JobProcessingServer
from src.stats.eventbus import Listener
from src.stats.metrics import QueueSizeMetric, LoadMetric, JobProcessTimeMetric
from src.systemtime import Stopwatch


class SimulationStatistics(Listener):

    def __init__(self, queue: JobStorage, servers: List[JobProcessingServer]) -> None:
        self._job_processing_metrics = []
        self._load_metric = LoadMetric()
        self._queue_size_metric = QueueSizeMetric()

        self._queue = queue
        self._servers = servers

        self._job_processing_time_dict = {}  # id to stopwatch

    def job_schedule(self, job: Job):
        print("SimulationStatistics: {} scheduled".format(job))
        self._record_queue_size()
        self._record_load()

    def job_processing_aborted(self, job):
        print("SimulationStatistics: {} processing aborted".format(job))
        del self._job_processing_time_dict[job.id]

    def job_process_start(self, job):
        self._job_processing_time_dict[job.id] = Stopwatch()
        print("SimulationStatistics: {} processing started".format(job))

    def job_was_processed(self, job):
        self._record_queue_size()
        self._record_load()

        stopwatch = self._job_processing_time_dict[job.id]
        elapsed = stopwatch.elapsed()
        self._job_processing_metrics.append(JobProcessTimeMetric(job, elapsed))
        print("SimulationStatistics: {} processed for {}".format(job, elapsed))
        del self._job_processing_time_dict[job.id]

    def _record_load(self):
        jobs_number = 0
        for server in self._servers:
            if server.job is not None:
                jobs_number = jobs_number + 1
        queue_size = self._queue.size()
        jobs_number = jobs_number + queue_size
        self._load_metric.add(jobs_number)

    def _record_queue_size(self):
        queue_size = self._queue.size()
        self._queue_size_metric.add(queue_size)

    def get_general_stats(self):
        _, avg_process_time, _ = self._process_time()
        # _, avg_queue_time, _ = self._queue_time()
        avg_queue_size = self._queue_size()
        avg_load = self._load_stat()
        table = [
            ["Average job processing time", avg_process_time, "ms"],
            # ["Average time in queue", avg_queue_time, "ms"],
            ["Average queue size", avg_queue_size, "jobs in queue"],
            ["Average jobs number in the system", avg_load, "jobs"]
        ]
        return tabulate(table, numalign="right")

    def _process_time(self):
        stats = self._job_processing_metrics
        time_per_job = [stat.process_time for stat in stats]
        total_time = sum(time_per_job)
        job_number = len(time_per_job)
        print(job_number)
        avg_time = total_time / job_number
        return total_time, avg_time, job_number

    # def _queue_time(self):
    #     stats = self._wait_time_metrics
    #     time_per_job = [stat.wait_time for stat in stats]
    #     total_time = sum(time_per_job)
    #     queued_jobs_number = len(time_per_job)
    #     avg_time = total_time / queued_jobs_number if queued_jobs_number is not 0 else 0
    #     return total_time, avg_time, queued_jobs_number

    def _queue_size(self):
        return self._queue_size_metric.average_queue_size()

    def _load_stat(self):
        return self._load_metric.average_load()
