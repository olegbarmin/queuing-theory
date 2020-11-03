import sys
from random import random

from src.configuration import ConfigReader
from src.job.jobs import JobGenerator, AtomicInteger
from src.job.queue import JobsQueue
from src.job.server import JobProcessingServer
from src.model import QueuingSystem

if __name__ == '__main__':
    conf_path = sys.argv[1]
    config = ConfigReader(conf_path)

    input_dist = config.input_distribution
    time_dist = config.process_time_distribution

    id_gen = AtomicInteger()
    job_generator = JobGenerator(lambda: id_gen.increment(), lambda: int(random() * 10))

    queue = JobsQueue(config.queue_size)
    servers = [JobProcessingServer(time_dist, queue, i + 1) for i in range(config.servers_number)]
    system = QueuingSystem(input_dist, job_generator, config.simulation_duration, servers, queue)

    system.start()
