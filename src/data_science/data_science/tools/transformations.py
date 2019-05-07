import datetime


def iso_to_datetime(isotime):
    """
    Transform isotime to datetime.
        :param isotime: isotime
    """
    if len(isotime) == 24:
        time = datetime.datetime.strptime(isotime.replace('Z', ''),
                                          '%Y-%m-%dT%H:%M:%S.%f')
    elif len(isotime) == 20:
        time = datetime.datetime.strptime(isotime.replace('Z', ''),
                                          '%Y-%m-%dT%H:%M:%S')
    else:
        raise ValueError('The provided string has a wrong format.')
    return time


def string_to_datetime(str_time, str_format=r'%Y-%m-%d %H:%M:%S'):
    """
    docstring here
        :param str_time: time in string format
        :param format='%Y-%m-%d%H:%M:%S': format definition
    """
    return datetime.datetime.strptime(str_time, str_format)


def per_hour_to_per_second(per_hour):
    """
    Transform a per hour rate to a per second rate.
        :param per_hour: quantity per hour
    """
    return per_hour / 3600


def seconds_to_hours(seconds):
    """
    Transform seconds to hours.
        :param seconds: number of seconds
    """
    return seconds / 3600


def range_to_range_linear(value, min_old_range, max_old_range, min_new_range,
                          max_new_range):
    """
    Transform a value from one range to another linearly.
        :param value: quantity to be transformed
        :param min_old_range: min
        :param max_old_range: max
        :param min_new_range: min
        :param max_new_range: max
    """
    if value < min_old_range:
        value = min_old_range
    elif value > max_old_range:
        value = max_old_range
    temp = ((value - min_old_range) / (max_old_range - min_old_range)) * \
           (max_new_range - min_new_range) + min_new_range
    return temp


def celcius_to_kelvin(celcius):
    return celcius + 273.15
