import threading

from data_science.simulation.time import TimeSimulator


class StoppableThread(threading.Thread):
    """
    Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition.
    """

    def __init__(self, target=None):
        if target is None:
            super(StoppableThread, self).__init__()
        else:
            super(StoppableThread, self).__init__(target=target)
        self._stop_event = threading.Event()

    def stop(self):
        """
        Stop the thread.
            :param self: self
        """
        self._stop_event.set()

    def stopped(self):
        """
        The stop event was triggered.
            :param self: self
        """
        return self._stop_event.is_set()


class ThreadableClass():
    """A class to provide threading functionality. Just overwriting run()."""

    def __init__(self, update_time=0.5):
        self.update_time = update_time
        self.time_sim = TimeSimulator()

    def do_something(self):
        pass

    def run(self):
        while True:
            if self.time_sim.tick(self.update_time):
                self.do_something()
                if self.thread.stopped():
                    break

    def start(self):
        """
        Start the thread.
            :param self: self
        """
        self.thread = StoppableThread(target=self.run)
        self.thread.start()

    def stop(self):
        """
        Stop the thread.
            :param self: self
        """
        self.thread.stop()
        self.thread.join()