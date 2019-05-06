# Functions to manipulate dataframes


def remove_row(df, row, reindex=True, ignore_error=True):
    """
    Remove a row from a dataframe
        :param df: dataframe
        :param row: row number
        :param reindex=True: reindex from zero
    """
    index_name = df.index.name
    try:
        df.drop([row], inplace=True)
    except:
        if ignore_error:
            pass
        else:
            raise KeyError('The dataframe does not contain a row with the \
                            specified index.')
    if reindex:
        df.reset_index(drop=True, inplace=True)
    if index_name:
        df.index.name = index_name
    return df


def drop_column(df, column, ignore_error=True):
    try:
        df.drop([column], inplace=True, axis=1)
    except:
        if ignore_error:
            pass
        else:
            raise KeyError('The dataframe does not contain a column with that \
                            name.')


def normalize_column(df, column):
    from sklearn import preprocessing

    min_max_scaler = preprocessing.MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(df[[column]].values.astype(float))
    return x_scaled


def column_derivative(df, time_column, value_column):
    import numpy as np

    return np.gradient(df[value_column], df[time_column])


def column_second_derivative(df, time_column, value_column):
    import numpy as np

    return np.gradient(np.gradient(df[value_column], df[time_column]),
                       df[time_column])


def write_to_csv(df, file_name, index_column_name='index'):
    df.to_csv(file_name, sep=';', index_label=index_column_name)


def read_from_csv(file_path, to_datetime=True, index_column_name='index',
                  time_format='%Y-%m-%d %H:%M:%S'):
    import pandas as pd
    from data_science.tools.transformations import string_to_datetime

    def funct(x):
        try:
            if type(x) is str:
                x = string_to_datetime(x, str_format=time_format)
        except:
            pass
        return x

    df = pd.read_csv(file_path, sep=';', index_col=[0])
    if to_datetime:
        for column in df.columns:
            if (column[-3:] == '_ts') or (column == 'timestamp'):
                df[column] = df[column].apply(lambda x: funct(x))

    # drop columns that pandas add by mistake
    drop_columns = ['level_0', 'level_1', 'index.0', 'index.1']
    for column in drop_columns:
        drop_column(df, column)
    return df
