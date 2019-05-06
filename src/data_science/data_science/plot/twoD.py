import matplotlib.pyplot as plt
import pandas as pd
import collections
import numpy as np
from data_science.plot.color import set_color_cycle


def simple_df(df, x_column, y_column, start=0, end=1, fig_size=(6, 4),
              color='blue', marker='o', label='', title='',
              legend='upper left'):
    """
    Plot a 2D graph from a pandas dataframe.
        :param df: a pandas dataframe
        :param x_column: name of the column containing X
        :param y_column: name of the column containing Y
        :param start: value from 0 to 1. defines the starting position in the
                        series
        :param end: value from 0 to 1. defines the ending position in the
                        series
        :param fig_size: size of the figure
        :param color: color for the plot
        :param marker: marker for the plot
        :param label: label for the plot
        :param title: title for the plot
        :param legen: legend for the plot
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError('df must be a DataFrame.')
    if not isinstance(x_column, str):
        raise TypeError('x_column must be an str')
    if not isinstance(y_column, str):
        raise TypeError('y_column must be an str')
    if (end < start) or (end < 0) or (end > 1) or (start < 0) or (start > 1):
        raise ValueError('end or start have wrong values')
    # # take care of the NaNs
    # df_temp = df[[x_column, y_column]].copy()
    # df_temp.dropna(inplace=True)

    # section of the data to plot
    start = int(df.shape[0] * start)
    end = int(df.shape[0] * end)

    # figure size and plot
    fig = plt.figure(figsize=fig_size)
    ax = plt.subplot(111)

    if label == '':
        label = y_column
    plt.plot(df[x_column][start:end], df[y_column][start:end],
             marker=marker, c=color, label=label)
    # del df_temp

    # labels and title
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.legend(loc=legend)
    if title == '':
        plt.title(x_column + ' vs. ' + y_column)
    else:
        plt.title(title)

    return fig, ax


def multiple_df(df, x_column, y_columns, start=0, end=1, fig_size=(6, 4),
                title='', legend='upper left', color_cycle=0, linestyle='-',
                grid=True, y_lim=None):
    """
    Plot a 2D graph from a pandas dataframe.
        :param df: a pandas dataframe
        :param x_column: name of the column containing X
        :param y_columns: list of the columns to be plot in Y
        :param start: value from 0 to 1. defines the starting position in the
                        series
        :param end: value from 0 to 1. defines the ending position in the
                        series
        :param fig_size: size of the figure
        :param color: color for the plot
        :param marker: marker for the plot
        :param label: label for the plot
        :param title: title for the plot
        :param legen: legend for the plot
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError('df must be a DataFrame.')
    if not isinstance(x_column, str):
        raise TypeError('x_column must be an str')
    if not isinstance(y_columns, list):
        y_columns = [y_columns]
    if not isinstance(y_columns[0], str):
        raise TypeError('y_columns must be a list of str')
    if (end < start) or (end < 0) or (end > 1) or (start < 0) or (start > 1):
        raise ValueError('end or start have wrong values')
    # # take care of the NaNs
    # columns = y_columns.copy()
    # columns.append(x_column)
    # df_temp = df[columns].copy()
    # df_temp.dropna(inplace=True)

    # section of the data to plot
    start = int(df.shape[0] * start)
    end = int(df.shape[0] * end)

    # figure size and plot
    fig = plt.figure(figsize=fig_size)

    ax = plt.subplot(111)

    # set color sequence
    set_color_cycle(color_cycle, ax)

    for column in y_columns:
        plt.plot(df[x_column][start:end], df[column][start:end],
                 label=column, linestyle=linestyle)

    # del df_temp

    # grid, labels and title
    if y_lim is not None:
        plt.ylim(y_lim)
    plt.grid(grid)
    plt.xlabel(x_column)
    plt.ylabel('upper variables')
    plt.legend(loc=legend)
    if title == '':
        plt.title(x_column + ' vs. multiple variables')
    else:
        plt.title(title)
    leg = plt.legend(loc=legend, ncol=2, mode="expand", shadow=True,
                     fancybox=True)
    leg.get_frame().set_alpha(0.5)

    return fig, ax


def multiple_second_axis_df(df, x_column, y_columns, fig, ax, start=0, end=1,
                            legend='lower left', color_cycle=0,
                            linestyle='--', grid=False):
    if not isinstance(df, pd.DataFrame):
        raise TypeError('df must be a DataFrame.')
    if not isinstance(x_column, str):
        raise TypeError('x_column must be an str')
    if not isinstance(y_columns, list):
        y_columns = [y_columns]
    if not isinstance(y_columns[0], str):
        raise TypeError('y_columns must be a list of str')
    if (end < start) or (end < 0) or (end > 1) or (start < 0) or (start > 1):
        raise ValueError('end or start have wrong values')
    # # take care of the NaNs
    # columns = y_columns.copy()
    # columns.append(x_column)
    # df_temp = df[columns].copy()
    # df_temp.dropna(inplace=True)

    # section of the data to plot
    start = int(df.shape[0] * start)
    end = int(df.shape[0] * end)

    # figure size and plot
    ax2 = ax.twinx()

    # set color sequence
    set_color_cycle(color_cycle, ax2)

    for column in y_columns:
        ax2.plot(df[x_column][start:end], df[column][start:end],
                 label=column, linestyle=linestyle)

    # del df_temp

    # grid, labels and title
    ax2.grid(grid)
    if len(y_columns) == 1:
        ax2.set_ylabel(y_columns[0])
    else:
        ax2.set_ylabel('bottom variables')

    leg = plt.legend(loc=legend, ncol=2, mode="expand", shadow=True,
                     fancybox=True)
    leg.get_frame().set_alpha(0.5)

    fig.tight_layout()


def shade_regions_df(df, x_column, condition_column, fig, ax, condition,
                     start=0, end=1, min_v=0, max_v=1, color='black',
                     transparence=0.75):
    import matplotlib.transforms as mtransforms

    # section of the data to plot
    start = int(df.shape[0] * start)
    end = int(df.shape[0] * end)

    trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    ax.fill_between(df[x_column][start:end], min_v, max_v,
                    where=condition(df[condition_column][start:end]),
                    facecolor='green', alpha=transparence, transform=trans,
                    color=color)


def simple(y_list, x_list=None, fig_size=(6, 4), color='blue', marker='o',
           label='', x_label='', y_label='', title='', legend='upper left'):
    """
    Plot a 2D graph from a list
        :param y_list: list containing Y
        :param x_list: list containing X
        :param fig_size: size of the figure
        :param color: color for the plot
        :param marker: marker for the plot
        :param label: label for the plot
        :param x_label: label for the x axis
        :param y_label: label for the y axis
        :param title: title for the plot
        :param legen: legend for the plot
    """
    if not isinstance(y_list, collections.Iterable):
        raise TypeError('y_column must be iterable')
    if x_list is not None:
        if not isinstance(x_list, collections.Iterable):
            raise TypeError('y_column must be iterable')
    else:
        x_list = np.arange(len(y_list))

    # figure size and plot
    plt.figure(figsize=fig_size)
    plt.plot(x_list, y_list, marker=marker, c=color, label=label)
    # labels and title
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend(loc=legend)
    plt.title(title)


def optimal_bins_number(lst):
    from scipy.stats import iqr
    from math import pow

    if isinstance(lst, list):
        lst = pd.Series(lst)

    bin_width = 2 * iqr(lst) * pow(len(lst), -1/3)
    return int((lst.max() - lst.min()) / bin_width)


def histogram(df, parameters, bins=None, start=0, end=1, regularize=False,
              fig_size=(6, 4), title='', legend='upper left'):
    from data_science.tools.transformations import range_to_range_linear

    if not isinstance(df, pd.DataFrame):
        raise TypeError('df must be a DataFrame.')
    if not isinstance(parameters, list):
        parameters = [parameters]
    if not isinstance(parameters[0], str):
        raise TypeError('y_columns must be a list of str')
    if (end < start) or (end < 0) or (end > 1) or (start < 0) or (start > 1):
        raise ValueError('end or start have wrong values')
    # # take care of the NaNs
    # df_temp = df[parameters].copy()
    # df_temp.dropna(inplace=True)

    # Regularize
    if regularize:
        for parameter in parameters:
            df[parameter] = df[parameter].apply(
                    lambda x: range_to_range_linear(x,
                                                    df[parameter].min(),
                                                    df[parameter].max(),
                                                    0,
                                                    100))

    # section of the data to plot
    start = int(df.shape[0] * start)
    end = int(df.shape[0] * end)

    # Rule of thumb for optimal number of bins
    if bins is None:
        bins = []
        for parameter in parameters:
            bins.append(optimal_bins_number(df[parameter][start:end]))
        bins = int(sum(bins)/len(bins))

    # figure size and plot
    fig = plt.figure(figsize=fig_size)

    ax = plt.subplot(111)
    for parameter in parameters:
        plt.hist(df[parameter][start:end], bins, label=parameter,
                 alpha=0.75)

    # del df_temp

    # labels and title
    plt.xlabel('bins')
    plt.ylabel('frequency')
    plt.legend(loc=legend)
    if title == '':
        plt.title('Histogram')
    else:
        plt.title(title)
    leg = plt.legend(loc=legend, ncol=2, mode="expand", shadow=True,
                     fancybox=True)
    leg.get_frame().set_alpha(0.5)

    return fig, ax


def show(font_size=20):
    """
    Display a figure.
    """
    plt.rcParams.update({'font.size': font_size})
    plt.show()
