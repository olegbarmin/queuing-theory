import sys
from random import random

from src.configuration import ConfigReader
from src.job.jobs import JobGenerator, AtomicInteger
from src.job.manager import ServerLoadManager
from src.job.queue import JobStorage
from src.job.server import JobProcessingServer
from src.model import QueuingSystem
from src.stats import SimulationStatistics

if __name__ == '__main__':
    conf_path = sys.argv[1]
    config = ConfigReader(conf_path)

    input_dist = config.input_distribution
    time_dist = config.process_time_distribution

    id_gen = AtomicInteger()
    job_generator = JobGenerator(lambda: id_gen.increment(), lambda: int(random() * 10))

    servers = [JobProcessingServer(time_dist, i + 1) for i in range(config.servers_number)]

    queue = JobStorage(config.queue_size)
    manager = ServerLoadManager(servers, queue)

    system = QueuingSystem(input_dist, job_generator, config.simulation_duration, servers, manager)
    system.start()

    stats = SimulationStatistics()
    for server in servers:
        stats.add_server_processing_metrics(server.stats)
    stats.add_wait_time_metrics(queue.stats)

    table = stats.get_server_processing_stats()
    print("------- Job Processing Time Stats -------")
    print(table)

    table = stats.get_wait_time_stats()
    print("------- Job Wait Time Stats -------")
    print(table)
