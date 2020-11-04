from typing import List

from tabulate import tabulate

from src.job.queue import WaitTimeMetric
from src.job.server import JobProcessTimeMetric


class SimulationStatistics:

    def __init__(self) -> None:
        self._job_processing_metrics = []
        self._wait_time_metrics = []

    def add_server_processing_metrics(self, metrics: List[JobProcessTimeMetric]):
        self._job_processing_metrics.extend(metrics)

    def add_wait_time_metrics(self, metrics: List[WaitTimeMetric]):
        self._wait_time_metrics.extend(metrics)

    def get_server_processing_stats(self):
        stats = self._job_processing_metrics
        time_per_job = [stat.process_time for stat in stats]

        total_time = sum(time_per_job)
        job_number = len(time_per_job)
        avg_time = total_time / job_number
        table = [
            ["Total time", total_time],
            ["Avg. time", avg_time],
            ["Total processed jobs number", job_number]
        ]
        return tabulate(table, numalign="right")

    def get_wait_time_stats(self):
        stats = self._wait_time_metrics
        time_per_job = [stat.wait_time for stat in stats]

        total_time = sum(time_per_job)
        queued_jobs_number = len(time_per_job)
        avg_time = total_time / queued_jobs_number if queued_jobs_number is not 0 else 0
        table = [
            ["Total time", total_time],
            ["Avg. time", avg_time],
            ["Total processed jobs number", queued_jobs_number]
        ]
        return tabulate(table, numalign="right")
