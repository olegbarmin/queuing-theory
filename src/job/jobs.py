import threading


class Job:

    def __init__(self, id, priority) -> None:
        self._id = id
        self._priority = priority

    @property
    def id(self):
        return self._id

    @property
    def priority(self):
        return self._priority

    def __str__(self) -> str:
        return "Job(id: {}, priority: {})".format(self._id, self._priority)

    def __eq__(self, o: object) -> bool:
        return self._id is o.id if isinstance(o, Job) else super().__eq__(o)

    def __lt__(self, other):
        return self._priority < other.priority


class AtomicInteger:

    def __init__(self, init_value: int = 0) -> None:
        self._val = init_value
        self._lock = threading.Lock()

    def increment(self) -> int:
        with self._lock:
            self._val = self._val + 1
            return self._val


class JobGenerator:

    def __init__(self, id_generation_func, priority_generation_func) -> None:
        self.priority_func = priority_generation_func
        self.id_func = id_generation_func

    def next(self) -> Job:
        id_ = self.id_func()
        priority = self.priority_func()
        if not isinstance(priority, int):
            raise Exception("Priority should be an integer. Actual: {}".format(priority))
        job = Job(id_, priority)
        print("JobGenerator: Generated job - {}".format(job))
        return job
