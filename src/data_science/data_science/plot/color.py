"""
Generates colors in a sequenced manner.
"""

import matplotlib.pyplot as plt
from cycler import cycler
import warnings


color_cycle = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black',
               'brown', 'aqua', 'olive']


def set_color_cycle(sequence, ax):
    if sequence == 0:
        ax.set_prop_cycle(cycler('color', color_cycle))
    elif sequence == 1:
        ax.set_prop_cycle(cycler('color', list(reversed(color_cycle))))


class _Brewer(object):
    """Encapsulates a nice sequence of colors.
    Shades of blue that look good in color and can be distinguished
    in grayscale (up to a point).

    Borrowed from http://colorbrewer2.org/
    """
    color_iter = None

    colors = ['#f7fbff', '#deebf7', '#c6dbef',
              '#9ecae1', '#6baed6', '#4292c6',
              '#2171b5', '#08519c', '#08306b'][::-1]

    # lists that indicate which colors to use depending on how many are used
    which_colors = [[],
                    [1],
                    [1, 3],
                    [0, 2, 4],
                    [0, 2, 4, 6],
                    [0, 2, 3, 5, 6],
                    [0, 2, 3, 4, 5, 6],
                    [0, 1, 2, 3, 4, 5, 6],
                    [0, 1, 2, 3, 4, 5, 6, 7],
                    [0, 1, 2, 3, 4, 5, 6, 7, 8],
                    ]

    current_figure = None

    @classmethod
    def Colors(cls):
        """Returns the list of colors.
        """
        return cls.colors

    @classmethod
    def ColorGenerator(cls, num):
        """Returns an iterator of color strings.
        n: how many colors will be used
        """
        for i in cls.which_colors[num]:
            yield cls.colors[i]
        raise StopIteration('Ran out of colors in _Brewer.')

    @classmethod
    def InitIter(cls, num):
        """Initializes the color iterator with the given number of colors."""
        cls.color_iter = cls.ColorGenerator(num)
        fig = plt.gcf()
        cls.current_figure = fig

    @classmethod
    def ClearIter(cls):
        """Sets the color iterator to None."""
        cls.color_iter = None
        cls.current_figure = None

    @classmethod
    def GetIter(cls, num):
        """Gets the color iterator."""
        fig = plt.gcf()
        if fig != cls.current_figure:
            cls.InitIter(num)
            cls.current_figure = fig

        if cls.color_iter is None:
            cls.InitIter(num)

        return cls.color_iter


def _UnderrideColor(options):
    """If color is not in the options, chooses a color.
    """
    if 'color' in options:
        return options

    # get the current color iterator; if there is none, init one
    color_iter = _Brewer.GetIter(5)

    try:
        options['color'] = next(color_iter)
    except StopIteration:
        # if you run out of colors, initialize the color iterator
        # and try again
        warnings.warn('Ran out of colors.  Starting over.')
        _Brewer.ClearIter()
        _UnderrideColor(options)

    return options
