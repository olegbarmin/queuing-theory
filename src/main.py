import sys
from random import random

from src.configuration import ConfigReader
from src.job.jobs import JobGenerator, AtomicInteger
from src.model import QueuingSystem

if __name__ == '__main__':
    conf_path = sys.argv[1]
    config = ConfigReader(conf_path)

    input_dist = config.input_distribution

    id_gen = AtomicInteger()
    job_generator = JobGenerator(lambda: id_gen.increment(), lambda: int(random() * 10))
    for i in range(10):
        print(job_generator.next())

    system = QueuingSystem(input_dist, job_generator, config.simulation_duration)
    system.start()
