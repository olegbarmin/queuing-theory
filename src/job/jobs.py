import threading


class Job:

    def __init__(self, id) -> None:
        self._id = id

    @property
    def id(self):
        return self._id

    def __str__(self) -> str:
        return "Job(id: {})".format(self._id)

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


class JobGenerator:

    def __init__(self, id_generation_func) -> None:
        self.id_func = id_generation_func

    def next(self) -> Job:
        id_ = self.id_func()
        job = Job(id_)
        print("JobGenerator: Generated job - {}".format(job))
        return job
