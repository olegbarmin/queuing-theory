import threading
from enum import Enum

import numpy as np


class JobTypes(Enum):
    SHOW_PRODUCTS = 'show_products'
    CHECKOUT = 'checkout'
    PAYMENT = 'payment'


class Job:

    def __init__(self, id_: int, type: JobTypes) -> None:
        self._id = id_
        self._type = type

    @property
    def id(self):
        return self._id

    def __str__(self) -> str:
        return f"Job(id: {self._id}, type: {self._type.name})"

    def __eq__(self, o: object) -> bool:
        return self._id is o.id if isinstance(o, Job) else super().__eq__(o)


class AtomicInteger:

    def __init__(self, init_value: int = 0) -> None:
        self._val = init_value
        self._lock = threading.Lock()

    def increment(self) -> int:
        with self._lock:
            self._val = self._val + 1
            return self._val


def type_generation() -> JobTypes:
    types_ = [JobTypes.SHOW_PRODUCTS, JobTypes.CHECKOUT, JobTypes.PAYMENT]
    return np.random.choice(types_, 1, p=[0.85, 0.1, 0.05])[0]


class JobGenerator:

    def __init__(self, id_generation_func, type_generation_func) -> None:
        self.id_func = id_generation_func
        self.type_func = type_generation_func

    def next(self) -> Job:
        id_ = self.id_func()
        type_ = self.type_func()

        job = Job(id_, type_)
        print(f"JobGenerator: Generated job - {job}")
        return job
