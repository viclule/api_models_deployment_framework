"""Tools to communicate with NI Devices."""
from settings import PLATFORM, WINDOWS


if PLATFORM == WINDOWS:
    from data_science.in_out.channels import ChannelTypes as CT
    import nidaqmx
    import sys

    class NIDevices:
        """A communication interface with NI devices."""

        def __init__(self):
            """Initialize the communication."""
            self.system = nidaqmx.system.System.local()
            self.ai_vol_channels = []
            self.ai_cur_channels = []
            self.ao_vol_channels = []
            self.ao_cur_channels = []
            self.di_channels = []
            self.do_channels = []

        def available_devices(self):
            """Return a list of the available devices."""
            return self.system.devices

        def ai_vol_channel(self, module, channel, sample_rate=1000,
                           no_samples=2):
            if no_samples < 2:
                no_samples = 2
            physical_channel = self.physical_channel(module, channel)
            # verify the channel exists physically
            result = self.verify_physical_channel(physical_channel, CT.VOLTAGE)
            if result:
                # add to the channel lists if not yet there
                channel = NIChannel(physical_channel, physical_channel)
                self.add_channel(channel, CT.VOLTAGE)
                # read the channel
                with nidaqmx.Task() as task:
                    task.ai_channels.add_ai_voltage_chan(physical_channel)
                    task.timing.cfg_samp_clk_timing(sample_rate,
                                                    samps_per_chan=no_samples)
                    task.timing.samp_timing_type = \
                        nidaqmx.constants.SampleTimingType.SAMPLE_CLOCK
                    values = task.read(
                        number_of_samples_per_channel=no_samples)
                    return sum(values) / float(len(values))
            else:
                return 'Channel can not be added.'

        def ao_vol_channel(self, value, module, channel, sample_rate=1000):
            if not hasattr(value, '__iter__'):
                value = [value, value]
            physical_channel = self.physical_channel(module, channel)
            # verify the channel exists physically
            result = self.verify_physical_channel(physical_channel, CT.VOLTAGE,
                                                  output=True)
            if result:
                # add to the channel lists if not yet there
                channel = NIChannel(physical_channel, physical_channel)
                self.add_channel(channel, CT.VOLTAGE, output=True)
                # write the channel
                with nidaqmx.Task() as task:
                    task.ao_channels.add_ao_voltage_chan(physical_channel)
                    task.timing.cfg_samp_clk_timing(sample_rate,
                                                    samps_per_chan=len(value))
                    task.timing.samp_timing_type = \
                        nidaqmx.constants.SampleTimingType.SAMPLE_CLOCK
                    task.write(value, auto_start=True)
            else:
                return 'Channel can not be added.'

        def verify_physical_channel(self, physical_channel, channel_type,
                                    output=False):
            try:
                with nidaqmx.Task() as task:
                    if not output:
                        if channel_type == CT.VOLTAGE:
                            task.ai_channels.add_ai_voltage_chan(
                                physical_channel)
                        elif channel_type == CT.CURRENT:
                            task.ai_channels.add_ai_current_chan(
                                physical_channel)
                    else:
                        if channel_type == CT.VOLTAGE:
                            task.ao_channels.add_ao_voltage_chan(
                                physical_channel)
                        elif channel_type == CT.CURRENT:
                            task.ao_channels.add_ao_current_chan(
                                physical_channel)
                return True
            except Exception as ex:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print('Line: ', exc_traceback.tb_lineno,
                      '. Error: The channel cannot be added. ', ex)
                return False

        def add_channel(self, channel, channel_type, output=False):
            if not output:
                if channel_type == CT.VOLTAGE:
                    if not self.is_channel_in_list(channel,
                                                   self.ai_vol_channels):
                        self.ai_vol_channels.append(channel)
                if channel_type == CT.CURRENT:
                    if not self.is_channel_in_list(channel,
                                                   self.ai_cur_channels):
                        self.ai_cur_channels.append(channel)

        def is_channel_in_list(self, channel, channel_list):
            for ch in channel_list:
                if (ch.name == channel.name) or \
                   (ch.physical_channel_name == channel.physical_channel_name):
                    return True
            return False

        def physical_channel(self, module, channel):
            return module + '/' + channel

    class NIChannel:
        """A representation of an analog input channel."""

        def __init__(self, name, physical_channel_name):
            """Initialize the communication.

                :param self: self
                :param name: channel name
                :param physical_channel_name: example: 'cDAQ1Mod1/ai0'
            """
            self.name = name
            self.physical_channel_name = physical_channel_name

        def __repr__(self):
            """Return a representation of the function."""
            return (f'{self.__class__.__name__}('
                    f'{self.name!r})')
