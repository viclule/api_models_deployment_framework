# Functions to generate empty dataframes for projects getting data from
# Cumulocity that is then transfered to the Data_API
import pandas as pd


def _pump_data():
    return [
        'pump_model',
        'serial_number',
        'name',
        'kind',             # development, long_test, customer, etc...
        'catalog_number',
        'c8y_id_1',         # device ID for this pump
        'c8y_id_2',         # each pump can have more than one
        'c8y_id_3',
        'c8y_id_4',
        ]


def pumps_data_empty_dataframe():
    """
    Generate an empty dataframe with the right columns.
    This dataframe contains the specific data of each pump.
    """
    pumps_data_df = pd.DataFrame(columns=_pump_data())
    pumps_data_df.index.name = 'pump_number'
    return pumps_data_df


def _datasets_data():
    return [
        'id',               # id of the dataset
        'timestamp',        # Time it was added
        'pump_number',      # assigned number for the pump
        'period',           # name of the period
        'period_start',     # in the format YYYYMM
        'period_end',       # in the format YYYYMM
        'comment',          # comment to this dataset
        ]


def datasets_data_empty_dataframe():
    """
    Generate an empty dataframe with the right columns.
    This dataframe contains the specific data of each dataset.
    """
    datasets_df = pd.DataFrame(columns=_datasets_data())
    datasets_df.index.name = 'dataset'
    return datasets_df


def _dataseries_content():
    return [
        'c8y_type',         # Type in c8y
        'c8y_id',           # device ID on which to find it (1, 2, 3 or 4).
                            # see pump_data
        'pump_location',
        'name',
        'kind',
        'units',
        'precision',
        ]


def dataseries_data_empty_dataframe():
    """
    Generate an empty dataframe with the right columns.
    This dataframe contains the specific data of each dataseries in a dataset.
    """
    dataseries_df = pd.DataFrame(columns=_dataseries_content())
    dataseries_df.index.name = 'parameter'
    return dataseries_df
