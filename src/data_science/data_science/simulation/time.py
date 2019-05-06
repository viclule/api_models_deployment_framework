import time


class TimeSimulator:
    """A simple time simulator.

    It provides an accelerated time stamp for simulation purposes.
    """

    def __init__(self, time_factor=1):
        """Initialize the Time_Simulator.

        Keyword arguments:
        time_factor -- how faster or slower is the time behaving
        """
        self.time_factor = time_factor
        self.initial_time = time.clock()
        self.temp_flag = False
        self.tick_last = 0

    def __repr__(self):
        """Return a representation of the function."""
        return (f'{self.__class__.__name__}('
                f'{self.time_factor!r})')

    def now(self):
        """Return the current time in seconds."""
        return (time.clock() - self.initial_time) * self.time_factor

    def reset(self):
        """Set timer back to zero."""
        self.initial_time = time.clock()
        self.tick_last = 0

    def tick(self, period):
        """Return a true flag every period.

        It has to run continuously.
        Keyword arguments:
        period -- how often the tick is delivered
        """
        # For faster executions purposes
        now = (time.clock() - self.initial_time) * self.time_factor
        if (now - self.tick_last) > period:
            self.tick_last = now
            return True
        else:
            return False
