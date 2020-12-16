from typing import List, Dict

from tabulate import tabulate

from src.job.jobs import Job
from src.job.manager import ServerLoadManager
from src.job.queue import JobStorage
from src.job.server import Server, ServerType
from src.stats.eventbus import Listener
from src.stats.metrics import QueueSizeMetric, LoadMetric, JobProcessTimeMetric, WaitTimeMetric, SystemBusynessMetric, \
    JobDropMetric
from src.systemtime import Stopwatch


class LoadManagerStatistics(Listener):

    def __init__(self, queue: JobStorage, servers: List[Server]) -> None:
        self._job_processing_metrics = []
        self._load_metric = LoadMetric()
        self._queue_size_metric = QueueSizeMetric()
        self._wait_time_metrics = []
        self._busyness_metric = SystemBusynessMetric()
        self._job_drop_metric = JobDropMetric()

        self._queue = queue
        self._servers = servers

        self._processing_time_dict = {}  # id to stopwatch
        self._queue_time_dict = {}  # id to stopwatch

    def job_arrived(self, job):
        self._job_drop_metric.record_job_arrival()

    def job_schedule(self, type, job: Job):
        print("SimulationStatistics: {} scheduled".format(job))
        self._record_queue_size()
        self._record_load()

        self._record_system_busy()

    def job_process_start(self, type, job: Job):
        self._processing_time_dict[job.id] = Stopwatch()
        print("SimulationStatistics: {} processing started".format(job))

    def job_was_processed(self, type, job):
        self._record_queue_size()
        self._record_load()

        self._record_job_finish(job)
        if self._is_system_idle():
            self._record_system_idle()

    def all_jobs_arrived(self):
        self._busyness_metric.stop_record()

    def job_queued(self, type, job: Job):
        print("SimulationStatistics: {} queued".format(job))
        self._queue_time_dict[job.id] = Stopwatch()

    def job_pop_from_queue(self, type, job: Job):
        print("SimulationStatistics: {} left queue".format(job))
        if job.id not in self._queue_time_dict:
            raise Exception("{} should be inside queue time dict, but it is not".format(job))
        stopwatch = self._queue_time_dict[job.id]
        elapsed = stopwatch.elapsed()
        self._wait_time_metrics.append(WaitTimeMetric(job, elapsed))
        del self._queue_time_dict[job.id]

    def job_rejected(self, type, job: Job):
        print(f"SimulationStatistics: {job} rejected")
        self._job_drop_metric.record_job_drop()

    def get_general_stats(self):
        _, avg_process_time, _ = self._process_time()
        _, avg_queue_time, _ = self._queue_time()
        avg_queue_size = self._queue_size()
        avg_load = self._load_stat()
        idle_probability = self._idle_probability()
        reject_probability = self._reject_probability()
        table = [
            ["Average job processing time", avg_process_time, "ms"],
            ["Average time in queue", avg_queue_time, "ms"],
            ["Average queue size", avg_queue_size, "jobs in queue"],
            ["Average jobs number in the system", avg_load, "jobs"],  # todo: extract to system stats
            ["Chance of system being idle", idle_probability, "%"],  # todo: extract to system stats
            ["Chance of reject", reject_probability, "%"]
        ]
        return tabulate(table, numalign="right")

    def _record_job_finish(self, job):
        stopwatch = self._processing_time_dict[job.id]
        elapsed = stopwatch.elapsed()
        self._job_processing_metrics.append(JobProcessTimeMetric(job, elapsed))
        print("SimulationStatistics: {} processed for {}".format(job, elapsed))
        del self._processing_time_dict[job.id]
        self._job_drop_metric.record_job_processed()

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

    def _process_time(self):
        stats = self._job_processing_metrics
        time_per_job = [stat.process_time for stat in stats]
        total_time = sum(time_per_job)
        job_number = len(time_per_job)
        avg_time = total_time / job_number
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

    def _load_stat(self):
        return self._load_metric.average_load()

    def _idle_probability(self) -> float:
        busy_time = self._busyness_metric.busy_time()
        idle_time = self._busyness_metric.idle_time()

        total_time = busy_time + idle_time
        print("SimulationStatistics: {} total time".format(total_time))

        return round((idle_time / total_time) * 100, 2)

    def _is_system_idle(self) -> bool:
        all_servers_idle = True
        for server in self._servers:
            if not server.is_idle:
                all_servers_idle = False
                break
        return self._queue.is_empty() and all_servers_idle

    def _record_system_idle(self):
        self._busyness_metric.record_idle()

    def _record_system_busy(self):
        self._busyness_metric.record_busy()

    def _reject_probability(self):
        return self._job_drop_metric.job_drop_chance()


class SimulationStatistics(Listener):

    def __init__(self, managers: Dict[ServerType, ServerLoadManager]) -> None:
        super().__init__()
        self._stats = {}
        self._managers = managers

    def job_arrived(self, job):
        for stats in self._stats.values():
            stats.job_arrived(job)

    def job_schedule(self, type, job):
        self._stats_for(type).job_schedule(type, job)

    def job_queued(self, type, job):
        self._stats_for(type).job_queued(type, job)

    def job_pop_from_queue(self, type, job):
        self._stats_for(type).job_pop_from_queue(type, job)

    def job_rejected(self, type, job):
        self._stats_for(type).job_rejected(type, job)

    def job_was_processed(self, type, job):
        self._stats_for(type).job_was_processed(type, job)

    def job_process_start(self, type, job):
        self._stats_for(type).job_process_start(type, job)

    def all_jobs_arrived(self):
        for stats in self._stats.values():
            stats.all_jobs_arrived()

    def _stats_for(self, type: ServerType) -> LoadManagerStatistics:
        if type not in self._stats:
            manager = self._managers[type]
            self._stats[type] = LoadManagerStatistics(manager.queue, manager.servers)
        return self._stats[type]

    def get_general_stats(self):
        return self._stats_for(ServerType.GATEWAY).get_general_stats()
