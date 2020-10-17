import numpy as np
import matplotlib.pyplot as plt

from distribution import ErlangDistribution

if __name__ == '__main__':
    erlang = ErlangDistribution(2, 1)

    x_values = np.linspace(0, 20, num=1000)
    y_values = [erlang.pdf(x) for x in x_values]

    plt.plot(x_values, y_values)
    plt.show()

