from random import random

import matplotlib.pyplot as plt

from configuration import ConfigReader
from jobs import JobGenerator, AtomicInteger

if __name__ == '__main__':
    config = ConfigReader("conf.yaml")

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

    id_gen = AtomicInteger()
    job_generator = JobGenerator(lambda: id_gen.increment(), lambda: int(random() * 10))
    for i in range(10):
        print(job_generator.next())
