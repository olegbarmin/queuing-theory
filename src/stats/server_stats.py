from typing import List

from tabulate import tabulate

from src.job.jobs import Job
from src.job.queue import JobStorage
from src.job.server import Server
from src.stats.eventbus import Listener
from src.stats.metrics import QueueSizeMetric, JobProcessTimeMetric, WaitTimeMetric
from src.systemtime import Stopwatch


class LoadManagerStatistics(Listener):

    def __init__(self, queue: JobStorage, servers: List[Server]) -> None:
        self._job_processing_metrics = []
        self._queue_size_metric = QueueSizeMetric()
        self._wait_time_metrics = []

        self._queue = queue
        self._servers = servers

        self._processing_time_dict = {}  # id to stopwatch
        self._queue_time_dict = {}  # id to stopwatch

    def job_schedule(self, type, job: Job):
        print("ServerStatistics: {} scheduled".format(job))
        self._record_queue_size()

    def job_process_start(self, type, job: Job):
        self._processing_time_dict[job.id] = Stopwatch()
        print("ServerStatistics: {} processing started".format(job))

    def job_was_processed(self, type, job):
        self._record_queue_size()
        self._record_job_finish(job)

    def job_queued(self, type, job: Job):
        print("ServerStatistics: {} queued".format(job))
        self._queue_time_dict[job.id] = Stopwatch()

    def job_pop_from_queue(self, type, job: Job):
        print("ServerStatistics: {} left queue".format(job))
        if job.id not in self._queue_time_dict:
            raise Exception("{} should be inside queue time dict, but it is not".format(job))
        stopwatch = self._queue_time_dict[job.id]
        elapsed = stopwatch.elapsed()
        self._wait_time_metrics.append(WaitTimeMetric(job, elapsed))
        del self._queue_time_dict[job.id]

    def get_general_stats(self):
        _, avg_process_time, _ = self._process_time()
        _, avg_queue_time, _ = self._queue_time()
        avg_queue_size = self._queue_size()
        table = [
            ["Average job processing time", avg_process_time, "ms"],
            ["Average time in queue", avg_queue_time, "ms"],
            ["Average queue size", avg_queue_size, "jobs in queue"],
        ]
        return tabulate(table, numalign="right")

    def _record_job_finish(self, job):
        stopwatch = self._processing_time_dict[job.id]
        elapsed = stopwatch.elapsed()
        self._job_processing_metrics.append(JobProcessTimeMetric(job, elapsed))
        print("ServerStatistics: {} processed for {}".format(job, elapsed))
        del self._processing_time_dict[job.id]

    def _record_queue_size(self):
        queue_size = self._queue.size()
        self._queue_size_metric.add(queue_size)

    def _process_time(self):
        stats = self._job_processing_metrics
        time_per_job = [stat.process_time for stat in stats]
        total_time = sum(time_per_job)
        job_number = len(time_per_job)
        avg_time = total_time / job_number if job_number != 0 else 0
        return total_time, avg_time, job_number

    def _queue_time(self):
        stats = self._wait_time_metrics
        time_per_job = [stat.wait_time for stat in stats]
        total_time = sum(time_per_job)
        queued_jobs_number = len(time_per_job)
        avg_time = total_time / queued_jobs_number if queued_jobs_number != 0 else 0
        return total_time, avg_time, queued_jobs_number

    def _queue_size(self):
        return self._queue_size_metric.average_queue_size()
