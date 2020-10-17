import math


class Distribution:

    def calc(self, x):
        pass


class ErlangDistribution(Distribution):

    def __init__(self, shape, rate) -> None:
        super().__init__()
        self.shape = shape  # k
        self.rate = rate  # lambda

    def calc(self, x):
        k = self.shape
        rate = self.rate

        numerator = rate ** k * x ** (k - 1) * math.exp(-(rate * x))
        denominator = math.factorial((k - 1))
        return numerator / denominator


class PoissonDistribution(Distribution):

    def __init__(self, rate) -> None:
        super().__init__()
        self.rate = rate  # lambda

