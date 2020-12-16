from typing import Dict

from tabulate import tabulate

from src.job.manager import ServerLoadManager
from src.job.server import ServerType
from src.stats.eventbus import Listener
from src.stats.metrics import JobDropMetric, LoadMetric
from src.stats.server_stats import LoadManagerStatistics


class SimulationStatistics(Listener):

    def __init__(self, managers: Dict[ServerType, ServerLoadManager]) -> None:
        super().__init__()
        self._stats = {t: m.stats for t, m in list(managers.items())}
        self._managers = managers

        self._load_metric = LoadMetric()
        self._job_drop_metric = JobDropMetric()

    def job_arrived(self, job):
        for stats in self._stats.values():
            stats.job_arrived(job)
        self._job_drop_metric.record_job_arrival()

    def job_schedule(self, type, job):
        self._stats_for(type).job_schedule(type, job)

    def job_queued(self, type, job):
        self._stats_for(type).job_queued(type, job)

    def job_pop_from_queue(self, type, job):
        self._stats_for(type).job_pop_from_queue(type, job)

    def job_rejected(self, type, job):
        for stats in self._stats.values():
            stats.job_rejected(type, job)
        self._load_metric.job_out()
        print(f"SimulationStatistics: {job} rejected")
        self._job_drop_metric.record_job_drop()

    def job_was_passed(self, job):
        self._stats_for(ServerType.GATEWAY).job_was_passed(job)

    def job_was_processed(self, type, job):
        self._load_metric.job_out()
        self._stats_for(type).job_was_processed(type, job)

    def job_process_start(self, type, job):
        self._stats_for(type).job_process_start(type, job)

    def all_jobs_arrived(self):
        for stats in self._stats.values():
            stats.all_jobs_arrived()
        self._load_metric.stop_record()

    def job_in(self):
        self._load_metric.job_in()

    def _stats_for(self, type: ServerType) -> LoadManagerStatistics:
        return self._stats[type]

    def print_stats(self):
        print(f"-------------------- System Statistics --------------------")
        avg_load = self._load_metric.average_load()
        idle_probability = self._load_metric.idle_probability()
        reject_probability = self._job_drop_metric.job_drop_chance()
        #
        table = tabulate([
            ["Average jobs number in the system", avg_load, "jobs"],
            ["Chance of system being idle", idle_probability, "%"],
            ["Chance of reject", reject_probability, "%"]
        ])
        print(table)

        for k in self._stats.keys():
            print(f"-------------------- {k} --------------------")
            table = str(self._stats_for(k).get_general_stats())
            print(table)

    # def _idle_probability(self) -> float:
    #     busy_time = self._busyness_metric.busy_time()
    #     idle_time = self._busyness_metric.idle_time()
    #
    #     total_time = busy_time + idle_time
    #     print("SimulationStatistics: {} total time".format(total_time))
    #
    #     return round((idle_time / total_time) * 100, 2)
