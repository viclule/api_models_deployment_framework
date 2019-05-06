"""Base classes."""
import weakref
import itertools


class InstanceTraceable:
    new_id = itertools.count()
    _instances = set()

    def __init__(self):
        self._instances.add(weakref.ref(self))
        self.id = next(__class__.new_id)

    @classmethod
    def getinstances(cls):
        dead = set()
        for ref in cls._instances:
            obj = ref()
            if obj is not None:
                yield obj
            else:
                dead.add(ref)
        cls._instances -= dead

    @classmethod
    def instance_exist(cls, name):
        instances = cls.getinstances()
        for inst in instances:
            if inst.name == name:
                return True, inst
        return False, inst

    @classmethod
    def getinstance(cls, name):
        instances = cls.getinstances()
        for inst in instances:
            if inst.name == name:
                return inst
        return None
