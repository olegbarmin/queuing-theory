import functools
import math
import random

import numpy as np


def production(function, stop: int, start: int = 1) -> float:
    """
    Calculates product of sequence build using given 'function' from 'start'
    to 'stop' inclusively.
    """
    values = [function(x) for x in range(start, stop + 1)]
    result = functools.reduce(lambda a, b: a * b, values)
    return result


class Distribution:

    def next_random(self) -> float:
        raise Exception("Method calc is not implemented for {} distribution".format(self.__class__.__name__))


class ErlangDistribution(Distribution):

    def __init__(self, shape, scale) -> None:
        super().__init__()
        if not isinstance(shape, int):
            raise Exception("Shape should be an integer for the Erlang Distribution")
        self._shape = shape  # alpha/m order of Distribution
        self._scale = float(scale)  # beta

        m = self._shape
        b = self._scale

        self._coefficient = (-b / m)  # is used each time to generate random number

    def next_random(self) -> float:
        prod = self._production()
        return self._coefficient * math.log(prod)

    def _production(self):
        m = self._shape
        return production(lambda x: random.random(), m)


class GammaDistribution(Distribution):

    def __init__(self, shape, scale) -> None:
        super().__init__()
        if shape < 0 or scale < 0:
            raise Exception("Both shape and scale of Gamma distribution must be greater than 0")

        self._shape = float(shape)  # k - shape parameter
        self._scale = float(scale)  # scale theta

    def next_random(self) -> float:
        """
        Ahrens-Dieter acceptance–rejection method
        https://en.wikipedia.org/wiki/Gamma_distribution#Generating_gamma-distributed_random_variables
        """
        return np.random.gamma(self._shape, self._scale)


class ExponentialDistribution(Distribution):

    def __init__(self, scale) -> None:
        super().__init__()
        self._scale = scale

    def next_random(self) -> float:
        r = random.random()
        return - self._scale * math.log(r)
