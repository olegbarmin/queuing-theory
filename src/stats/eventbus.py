import threading


class Listener:

    def job_schedule(self, job):
        pass

    def job_processing_aborted(self, job):
        pass

    def job_queued(self, job):
        pass

    def job_pop_from_queue(self, job):
        pass

    def job_dropped_from_queue(self, job):
        pass

    def job_was_processed(self, job):
        pass

    def job_process_start(self, job):
        pass


class EventBus:
    def __init__(self) -> None:
        self._listeners = []
        self._lock = threading.Lock()

    def add(self, listener: Listener):
        self._listeners.append(listener)

    def job_schedule(self, job):
        """
        Job was added into the queue or was sent to the server directly
        """
        with self._lock:
            for listener in self._listeners:
                listener.job_schedule(job)

    def job_processing_aborted(self, job):
        with self._lock:
            for listener in self._listeners:
                listener.job_processing_aborted(job)

    def job_queued(self, job):
        """
        Job was added into the queue
        """
        with self._lock:
            for listener in self._listeners:
                listener.job_queued(job)

    def job_pop_from_queue(self, job):
        with self._lock:
            for listener in self._listeners:
                listener.job_pop_from_queue(job)

    def job_dropped_from_queue(self, job):
        with self._lock:
            for listener in self._listeners:
                listener.job_dropped_from_queue(job)

    def job_process_start(self, job):
        """
        Job processing was started
        """
        with self._lock:
            for listener in self._listeners:
                listener.job_process_start(job)

    def job_was_processed(self, job):
        """
        Job was successfully processed
        """
        with self._lock:
            for listener in self._listeners:
                listener.job_was_processed(job)
