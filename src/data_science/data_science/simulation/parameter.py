"""Parameter to build devices."""
from collections import deque
import weakref
import itertools

from data_science.tools.classes import InstanceTraceable
import data_science.tools.transformations as transf
from data_science.tools.time import get_timestamp_unix


class Parameter(InstanceTraceable):
    """A parameter for building devices."""

    def __init__(self, name, value=0, units=None, auto_log=True):
        """Initialize the instance."""
        super().__init__()
        self.name = None
        if __class__.instance_exist(name):
            raise KeyError(f'The name {name} is already taken.')
        else:
            self.name = name
        self.value = value
        self.units = units
        self.auto_log = auto_log
        self.log = deque([])
        self.max_log_size = 100
        self.timestamp = None

    def update_value(self, value, log=False, raw=False):
        last_value = self.value
        self.value = value
        self.timestamp = get_timestamp_unix()
        if log or (self.auto_log and (last_value != self.value)):
            self.add_to_log()

    def add_to_log(self):
        """Log the current state.

        Keyword arguments:
        """
        if len(self.log) >= self.max_log_size:
            self.log.rotate(-1)
            self.log.pop()
        self.log.append((self.value, self.timestamp))

    def reset_log(self):
        """Restart the log lists."""
        self.log = deque([])

    @classmethod
    def getinstances(cls):
        instances = super().getinstances()
        sub_inst = []
        for inst in instances:
            if isinstance(inst, __class__):
                sub_inst.append(inst)
        return sub_inst

    @classmethod
    def instance_exist(cls, name):
        exist, inst = super().instance_exist(name)
        if isinstance(inst, __class__) and exist:
            return exist
        else:
            return False

    @classmethod
    def getinstance(cls, name):
        inst = super().getinstance(name)
        if isinstance(inst, __class__):
            return inst
        else:
            return None


# Not necessary so far
class NotConfiguredError(Exception):
    pass
