"""Generates profiles."""


class Profiles:
    """Profiles Functionality."""

    @staticmethod
    def screw_profile_generator(rev_second, samples_second, up_percentage,
                                up_level, down_level, seconds=1):
        """Generate a screw profile.
        
        Keyword arguments:
        rev_seconds --
        samples_second --
        up_percentage -- percentage of the rotor profile near to the housing.
                        One revolution looking like this.

                        _up_        

                            _down___ 
        up_level -- for example 9 V
        down_level -- for example 1 V
        seconds -- how many seconds of data to generate
        """
        data = []
        i = 0
        counter_up = 0
        counter_down = 0
        while i < samples_second * seconds:
            if counter_up < (up_percentage * samples_second) / rev_second:
                data.append(up_level)
                counter_up = counter_up + 1
            elif counter_up < \
                    ((1.0 - up_percentage) * samples_second) / rev_second:
                data.append(down_level)
                counter_down = counter_down + 1
                
            if counter_up >= (up_percentage * samples_second) / rev_second \
                    and counter_down >= \
                        (1.0 - up_percentage) * samples_second / rev_second:
                counter_up = 0
                counter_down = 0
            i = i + 1
        return data

    @staticmethod
    def linear_ramp_generator(start, end, samples_second, seconds=1):
        """Generate a linear profile..
        
        Keyword arguments:
        samples_second --
        start -- starting value
        end -- ending value
        seconds -- how many seconds of data to generate
        """
        data = []
        i = 0
        length = samples_second * seconds
        while i < length:
            data.append(start - (start - end) * (i / length))
            i = i + 1
        return data