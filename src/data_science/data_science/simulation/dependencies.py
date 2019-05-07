"""Dependencies that can be added to a device."""
import math

from data_science.tools.classes import InstanceTraceable


class Dependency(InstanceTraceable):
    """A dependency."""

    def __init__(self, name, first_parameter, second_parameter, a,
                 third_parameter=None, b=0, c=0, d=0, e=0):
        """Initialize the instance.

        Args:
        first_parameter - the name of the parameter to be updated
        second_parameter - the name of a parameter affecting the first
        """
        super().__init__()
        self.name = None
        if __class__.instance_exist(name):
            raise KeyError(f'The name {name} is already taken.')
        else:
            self.name = name
        self.first_parameter = first_parameter
        self.second_parameter = second_parameter
        self.third_parameter = third_parameter
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e

    def run(self, first_value, second_value, third_value=0):
        return second_value

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


class PolynomialDependency(Dependency):
    """A polynomial dependancy.

    Dependancy of the form: y = a + b*x + c*x^2 + d*x^3"""

    def run(self, first_value, second_value, third_value=0):
        """Dependancy of the form: y = a + b*x + c*x^2 + d*x^3"""
        value = self.a + second_value * self.b + second_value**2 * self.c + \
            + second_value**3 * self.d
        return value


class ExponentialDependency(Dependency):
    """An exponential dependancy.

    Dependancy of the form: y = a^x + b"""

    def run(self, first_value, second_value, third_value=0):
        """Dependancy of the form: y = a^x + b"""
        value = math.pow(self.a, second_value) + self.b
        return value


class FirstOrderDependancy(Dependency):
    """A first order system dependancy.

    Dependancy of the form: y = a + (b - a)*(1 - e^(-(x - d) / c)"""

    def run(self, first_value, second_value, third_value=0):
        """Dependancy of the form: y = a + (b - a)*(1 - e^(-(x - d) / c)"""
        value = self.a + (self.b - self.a) * \
            (1 - math.exp(-(second_value - self.d) / self.c))
        return value


class PIDDependancy(Dependency):
    """A PID dependency."""
    pass
