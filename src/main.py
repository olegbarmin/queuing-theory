import os
from pathlib import Path
from random import random

from src.configuration import ConfigReader
from src.job.jobs import JobGenerator, AtomicInteger
from src.job.manager import ServerLoadManager
from src.job.queue import JobStorage
from src.job.server import JobProcessingServer
from src.model import QueuingSystem
from src.stats import SimulationStatistics

if __name__ == '__main__':
    conf_path = os.path.join(str(Path(__file__).parent.parent.joinpath()), "conf.yaml")
    config = ConfigReader(conf_path)

    input_dist = config.input_distribution
    time_dist = config.process_time_distribution

    id_gen = AtomicInteger()
    job_generator = JobGenerator(lambda: id_gen.increment(), lambda: int(random() * 10) % 2 + 1)

    servers = [JobProcessingServer(time_dist, i + 1) for i in range(config.servers_number)]

    queue = JobStorage(config.queue_size)
    manager = ServerLoadManager(servers, queue)

    system = QueuingSystem(input_dist, job_generator, config.simulation_duration, servers, manager)
    system.run()

    stats = SimulationStatistics()
    for server in servers:
        stats.add_server_processing_metrics(server.stats)
    stats.add_wait_time_metrics(queue.stats)
    stats.add_manager_stats(manager.stats)

    table = stats.get_server_processing_stats()
    print("------- Job Processing Time Stats -------")
    print(table)

    table = stats.get_wait_time_stats()
    print("------- Job Wait Time Stats -------")
    print(table)

    table = stats.get_general_stats()
    print("------- General Stats -------")
    print(table)

    # todo: jobs in the system
    # todo: probability of system being idle
    # todo: probability of reject
