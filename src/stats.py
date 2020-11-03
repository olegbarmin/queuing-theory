from typing import List

from tabulate import tabulate

from src.job.server import JobProcessTimeMetric


class SimulationStatistics:

    def __init__(self) -> None:
        self.job_processing_metrics = []

    def add_server_processing_metrics(self, metrics: List[JobProcessTimeMetric]):
        self.job_processing_metrics.extend(metrics)

    def get_server_processing_stats(self):
        stats = self.job_processing_metrics
        job_process_times = [stat.process_time for stat in stats]

        total_time = sum(job_process_times)
        processed_job_number = len(job_process_times)
        avg_time = total_time / processed_job_number
        table = [
            ["Total time", total_time],
            ["Avg. time", avg_time],
            ["Total processed jobs number", processed_job_number]
        ]
        return tabulate(table, numalign="right")
