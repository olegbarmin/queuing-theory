import functools
import math
import random


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


class ExponentialDistribution(Distribution):

    def __init__(self, rate) -> None:
        super().__init__()
        self._rate = rate  # lambda

    def next_random(self) -> float:
        r = random.random()
        numerator = - math.log(r)
        denominator = self._rate
        return numerator / denominator
