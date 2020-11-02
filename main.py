import matplotlib.pyplot as plt

from distribution import ErlangDistribution

if __name__ == '__main__':
    dist = ErlangDistribution(2, 1)
    x = [dist.next_random() for _ in range(0, 10000)]
    plt.hist(x, 100)
    plt.show()
