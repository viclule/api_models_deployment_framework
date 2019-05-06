from collections import deque

from data_science.simulation.parameter import Parameter
from data_science.simulation.dependencies import Dependency
from data_science.tools.threading_utilities import ThreadableClass


class Device(ThreadableClass):
    """A base class for pumps."""

    def __init__(self, name, log=False, update_time=0.5):
        """Initialize the Pump Basic."""
        super().__init__(update_time=update_time)
        self.name = name
        self.log = log
        self.dependencies = []
        print('upd_time: ', self.update_time)

    def add_dependency(self, dependency_name):
        if dependency_name in self.dependencies:
            raise KeyError('The dependency {} was already added \
                           to this device.'.format(dependency_name))
        else:
            self.dependencies.append(dependency_name)

    def update_dependencies(self):
        """Run the dependencies, the order is relevant."""
        for dep_name in self.dependencies:
            dp = Dependency.getinstance(dep_name)
            if dp is not None:
                value = dp.run(self.get_parameter_value(dp.first_parameter),
                               self.get_parameter_value(dp.second_parameter))
                self.update_parameter(dp.first_parameter, value,
                                      run_dependencies=False)
            else:
                raise KeyError('The dependency {} is \
                               not defined.'.format(dep_name))

    def update_parameter(self, name, value, run_dependencies=True):
        parameter = Parameter.getinstance(name)
        if parameter is not None:
            parameter.update_value(value, log=self.log)
            if run_dependencies:
                self.update_dependencies()
        else:
            raise KeyError("The parameter {} does not exist.".format(name))

    def get_parameter_value(self, name):
        parameter = Parameter.getinstance(name)
        if parameter is not None:
            return parameter.value
        else:
            raise KeyError("The parameter {} does not exist.".format(name))

    def get_parameter(self, name):
        parameter = Parameter.getinstance(name)
        if parameter is not None:
            return parameter
        else:
            raise KeyError("The parameter {} does not exist.".format(name))

    def do_something(self):
        self.update_dependencies()


class Pump_Parameters:
    """Typical pump parameter."""

    inlet_pressure = 'inlet_pressure'
    water_flow = 'water_flow'
    clearance_primary = 'clearance_primary'
    clearance_secondary = 'clearance_secondary'
    bearing_temp = 'bearing_temp'
    inlet_temp = 'inlet_temp'
    outlet_temp = 'outlet_temp'
    water_inlet_temp = 'water_inlet_temp'
    water_outlet_temp = 'water_outlet_temp'
    frequency = 'frequency'
    power = 'power'
    time = 'time'
    gas_flow = 'gas_flow'
