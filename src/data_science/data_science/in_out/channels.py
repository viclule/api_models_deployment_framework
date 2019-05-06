from data_science.tools.threading_utilities import ThreadableClass
import data_science.tools.transformations as transf
from data_science.tools.classes import InstanceTraceable
from data_science.simulation.parameter import Parameter


class ChannelTypes():
    """Communication channel types."""

    UNDEFINED = "undefined"
    CURRENT = "current"
    VOLTAGE = "voltage"
    PT1000 = "pt1000"
    DIGITAL = "digital"

    @classmethod
    def get_types(cls):
        attrs = []
        for k, v in cls.__dict__.items():
            if isinstance(k, str) and isinstance(v, str) and k[0:2] != "__":
                attrs.append(v)
        return attrs


class Channel(InstanceTraceable):

    def __init__(self, physical, minimum, maximum, physical_minimum,
                 physical_maximum, name, parameter_name=None,
                 channel_type=ChannelTypes.UNDEFINED,
                 units='no_units', db_model=None):
        super().__init__()
        self.name = None
        if __class__.instance_exist(name):
            raise KeyError('The name {} is already taken.'.format(name))
        else:
            self.name = name
        self.physical = physical
        self.minimum = float(minimum)
        self.maximum = float(maximum)
        self.physical_minimum = float(physical_minimum)
        self.physical_maximum = float(physical_maximum)
        self.parameter_name = parameter_name
        self.channel_type = channel_type
        self.units = units
        self.db_model = db_model
        if self.channel_type == ChannelTypes.DIGITAL:
            self.value = False
        else:
            self.value = 0.0

    def set_minimum(self, minimum):
        self.minimum = float(minimum)

    def set_maximum(self, maximum):
        self.maximum = float(maximum)

    def set_physical_minimum(self, physical_minimum):
        self.physical_minimum = float(physical_minimum)

    def set_physical_maximum(self, physical_maximum):
        self.physical_maximum = float(physical_maximum)

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


class InputChannel(Channel):

    def read(self, raw=False):
        temp_value = self.physical()
        if (self.channel_type == ChannelTypes.VOLTAGE) or \
           (self.channel_type == ChannelTypes.CURRENT):
            if not raw:
                self.minimum = float(self.minimum)
                temp = transf.range_to_range_linear(temp_value,
                                                    self.physical_minimum,
                                                    self.physical_maximum,
                                                    self.minimum,
                                                    self.maximum)
            else:
                temp = temp_value
        else:
            temp = temp_value
        self.value = temp
        return temp


class OutputChannel(Channel):

    def write(self, value, raw=False):
        if self.db_model is not None:
            channel = self.db_model.objects.filter(name=self.name,
                                                   live=True).first()

        if (self.channel_type == ChannelTypes.VOLTAGE) or \
           (self.channel_type == ChannelTypes.CURRENT):
            if not raw:
                temp = transf.range_to_range_linear(value,
                                                    self.minimum,
                                                    self.maximum,
                                                    self.physical_minimum,
                                                    self.physical_maximum)
            else:
                temp = value
            temp = int(temp)
            if self.db_model is not None:
                channel.value_analog = temp
        else:
            temp = value
            if self.db_model is not None:
                channel.value_digital = temp
        self.physical(temp)
        self.value = temp

        if self.db_model is not None:
            channel.save()

    def read(self):
        if self.db_model is not None:
            channel = self.db_model.objects.filter(name=self.name,
                                                   live=True).first()
            if (self.channel_type == ChannelTypes.VOLTAGE) or \
               (self.channel_type == ChannelTypes.CURRENT):
                return channel.value_analog
            elif self.channel_type == ChannelTypes.DIGITAL:
                return channel.value_digital
            else:
                raise NotImplementedError('This type of channel is not \
                                          implemented yet.')
        else:
            return self.value


class ChannelsUpdater(ThreadableClass):
    """A class to update all physical channels in an StoppableThread."""

    def update_channels(self):
        instances = Channel.getinstances()
        for instance in instances:
            if instance.parameter_name is not None:
                parameter = Parameter.getinstance(instance.parameter_name)
                if isinstance(instance, InputChannel):
                    value = instance.read()
                    parameter.update_value(value)
                if isinstance(instance, OutputChannel):
                    instance.write(parameter.value)

    def do_something(self):
        while True:
            self.update_channels()
