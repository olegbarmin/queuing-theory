import threading


class Listener:

    def job_arrived(self, job):
        pass

    def job_schedule(self, _type, job):
        pass

    def job_queued(self, _type, job):
        pass

    def job_pop_from_queue(self, _type, job):
        pass

    def job_rejected(self, _type, job):
        pass

    def job_was_processed(self, _type, job):
        pass

    def job_process_start(self, _type, job):
        pass

    def all_jobs_arrived(self):
        pass

    def job_was_passed(self, job):
        pass

    def job_in(self):
        pass


class EventBus:
    def __init__(self) -> None:
        self._listeners = []
        self._lock = threading.Lock()

    def add(self, listener: Listener):
        self._listeners.append(listener)

    def job_arrived(self, job):
        with self._lock:
            for listener in self._listeners:
                listener.job_arrived(job)

    def job_schedule(self, _type, job):
        """
        Job was added into the queue or was sent to the server directly
        """
        with self._lock:
            for listener in self._listeners:
                listener.job_schedule(_type, job)

    def job_queued(self, _type, job):
        """
        Job was added into the queue
        """
        with self._lock:
            for listener in self._listeners:
                listener.job_queued(_type, job)

    def job_pop_from_queue(self, _type, job):
        with self._lock:
            for listener in self._listeners:
                listener.job_pop_from_queue(_type, job)

    def job_rejected(self, _type, job):
        with self._lock:
            for listener in self._listeners:
                listener.job_rejected(_type, job)

    def job_process_start(self, _type, job):
        """
        Job processing was started
        """
        with self._lock:
            for listener in self._listeners:
                listener.job_process_start(_type, job)

    def job_was_processed(self, _type, job):
        """
        Job was successfully processed
        """
        with self._lock:
            for listener in self._listeners:
                listener.job_was_processed(_type, job)

    def all_jobs_arrived(self):
        """
        All generated jobs were processed, and there wouldn't be more
        """
        with self._lock:
            for listener in self._listeners:
                listener.all_jobs_arrived()

    def job_was_passed(self, _type, job):
        with self._lock:
            for listener in self._listeners:
                listener.job_was_passed(job)

    def job_in(self):
        with self._lock:
            for listener in self._listeners:
                listener.job_in()
