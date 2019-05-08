"""Tools to communicate with Widgetlords Devices."""
from platform import PLATFORM, LINUX


if PLATFORM == LINUX:
    import widgetlords.pi_spi_din as wl

    class WidgetLords():

        def __init__(self):
            wl.init()

        def ai_module(self, chip_select):
            """
            Analog input module.

            Range for 0-10 V -> 0-3685
            Range for 4-20 mA -> 745-3723
                :param self: self
                :param chip_select: chip selected in the device
            """
            if not isinstance(chip_select, int):
                raise TypeError('chip_select must be an integer.')
            if (chip_select < 0) or (chip_select > 4):
                raise ValueError('invalid chip_select value.')
            if chip_select == 0:
                return wl.Mod8AI(wl.ChipEnable.CE0)
            if chip_select == 1:
                return wl.Mod8AI(wl.ChipEnable.CE1)
            if chip_select == 2:
                return wl.Mod8AI(wl.ChipEnable.CE2)
            if chip_select == 3:
                return wl.Mod8AI(wl.ChipEnable.CE3)
            if chip_select == 4:
                return wl.Mod8AI(wl.ChipEnable.CE4)

        def ao_module(self):
            return wl.Mod4AO()

        def do_module(self, chip_select):
            if not isinstance(chip_select, int):
                raise TypeError('chip_select must be an integer.')
            if (chip_select < 0) or (chip_select > 4):
                raise ValueError('invalid chip_select value.')
            if chip_select == 0:
                return wl.Mod4KO(wl.ChipEnable.CE0)
            if chip_select == 1:
                return wl.Mod4KO(wl.ChipEnable.CE1)
            if chip_select == 2:
                return wl.Mod4KO(wl.ChipEnable.CE2)
            if chip_select == 3:
                return wl.Mod4KO(wl.ChipEnable.CE3)
            if chip_select == 4:
                return wl.Mod4KO(wl.ChipEnable.CE4)

        def di_module(self, chip_select):
            if not isinstance(chip_select, int):
                raise TypeError('chip_select must be an integer.')
            if (chip_select < 0) or (chip_select > 4):
                raise ValueError('invalid chip_select value.')
            if chip_select == 0:
                return wl.Mod8DI(wl.ChipEnable.CE0)
            if chip_select == 1:
                return wl.Mod8DI(wl.ChipEnable.CE1)
            if chip_select == 2:
                return wl.Mod8DI(wl.ChipEnable.CE2)
            if chip_select == 3:
                return wl.Mod8DI(wl.ChipEnable.CE3)
            if chip_select == 4:
                return wl.Mod8DI(wl.ChipEnable.CE4)

        def ai_single(self, chip_select, channel):
            if not isinstance(channel, int):
                raise TypeError('channel must be an integer.')
            if (channel < 0) or (channel > 7):
                raise ValueError('invalid channel value.')
            inputs = self.ai_module(chip_select)
            value = inputs.read_single(channel)
            return value

        def ao_single(self, value, chip_select, channel):
            # chip_select is added only for consistency
            if not isinstance(channel, int):
                raise TypeError('channel must be an integer.')
            if (channel < 0) or (channel > 3):
                raise ValueError('invalid channel value.')
            outputs = self.ao_module()
            outputs.write_single(channel, value)
            return True

        def di_single(self, chip_select, channel):
            if not isinstance(channel, int):
                raise TypeError('channel must be an integer.')
            if (channel < 0) or (channel > 7):
                raise ValueError('invalid channel value.')
            inputs = self.di_module(chip_select)
            return inputs.read_single(channel)

        def do_single(self, value, chip_select, channel):
            if not isinstance(channel, int):
                raise TypeError('channel must be an integer.')
            if (channel < 0) or (channel > 3):
                raise ValueError('invalid channel value.')
            if not isinstance(value, bool):
                raise TypeError('value must be an integer.')
            relays = self.do_module(chip_select)
            relays.write_single(channel, value)
            return True
