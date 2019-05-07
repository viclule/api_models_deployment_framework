# some useful ideal gas relationships
import math


air_specific_heats_ratio = 1.4


def compression_polytropic_coefficient(inlet_temperature, inlet_pressure,
                                       outlet_temperature, outlet_pressure):
    """
    Polytropic coefficient in a compression process.
        :param inlet_temperature:
        :param inlet_pressure:
        :param outlet_temperature:
        :param outlet_pressure:
    """
    try:
        a = math.log(outlet_temperature / inlet_temperature,
                     outlet_pressure / inlet_pressure)
        return 1 / (1 - a)
    except ZeroDivisionError as e:
        print(e)
        return 1.0


def polytropic_compression_heat_proportion(polytropic_coefficient):
    return (air_specific_heats_ratio - polytropic_coefficient) / \
           (air_specific_heats_ratio - 1)
