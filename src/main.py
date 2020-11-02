import sys
from random import random

import matplotlib.pyplot as plt

from src.configuration import ConfigReader
from src.jobs import JobGenerator, AtomicInteger
from src.model import QueuingSystem

if __name__ == '__main__':
    conf_path = sys.argv[1]
    config = ConfigReader(conf_path)

    input_dist = config.input_distribution
    x = [input_dist.next_random() for _ in range(0, 100000)]
    print(max(x))
    print(sum(x) / len(x))
    plt.hist(x, 100)
    plt.title("InputDist")
    plt.show()

    process_time_dist = config.process_time_distribution
    x = [process_time_dist.next_random() for _ in range(0, 100000)]
    print(max(x))
    print(sum(x) / len(x))
    plt.hist(x, 100)
    plt.title("ProcessTimeDist")
    plt.show()

    print(config.servers_number)
    print(config.queue_size)
    print(config.simulation_duration)

    id_gen = AtomicInteger()
    job_generator = JobGenerator(lambda: id_gen.increment(), lambda: int(random() * 10))
    for i in range(10):
        print(job_generator.next())

    system = QueuingSystem(input_dist, job_generator, config.simulation_duration)
    system.start()
