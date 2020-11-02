import matplotlib.pyplot as plt

from configuration import ConfigReader

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


