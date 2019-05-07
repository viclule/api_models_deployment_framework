"""
Functions to transfer data between cumulocity.com and the data_api.
"""
from ipywidgets import FloatProgress

import data_science.data_transfer.data_api as api
import data_science.tools.time as tm


def generate_dataset(data_api, pumps_data_df, pump_number, period, comment):
    """
    Create a new dataset in the data_api based on the master dataset
    pumps_data_df information.
        :param data_api: instance of the class Data_API
        :param pumps_data_df: pandas dataframe based on
        :param pump_number: pump numeric identifier
        :param period: time period in the format YYYYMM
    """
    pump_data = pumps_data_df.loc[[pump_number]]
    dt = api.Dataset(data_api,
                     name=pump_data['name'].values[0],
                     pump_model=pump_data['pump_model'].values[0],
                     kind=pump_data['kind'].values[0],
                     description=str(pump_number) + ' - ' + period \
                     + ' - ' + comment,
                     serial_number=pump_data['serial_number'].values[0],
                     catalog_number=pump_data['catalog_number'].values[0]
                     )
    return dt.generate_id()


def generate_dataseries(data_api, dataset, dataseries_df):
    """
    Create the dataseries for a dataset.
        :param data_api: instance of the class Data_API
        :param dataset: instance of the class Dataset
        :param dataseries_df: pandas dataframe with the information
    """
    dataseries_id = []
    for row in dataseries_df.itertuples():
        ds = api.Dataseries(dataset_object=dataset,
                            kind=row.kind,
                            pump_location=row.pump_location,
                            name=row.name,
                            units=row.units,
                            precision=row.precision,
                            user=data_api.user,
                            numeric_identifier=row.Index
                            )
        ds_id = ds.generate_id()
        dataseries_id.append(ds_id)
    return dataseries_id


def generate_dataset_pump_and_time(data_api, pump_number, time_period, comment,
                                   pumps_data_df, dataseries_df):
    """
    Generate a dataset and its dataseries for a pump_number and time_period
        :param data_api: instance of the class Data_API
        :param pump_number: pump numeric identifier
        :param time_period: time period in the format YYYYMM
        :param comment: comment to this dataset
        :param pumps_data_df: pandas dataframe with the pumps data
        :param dataseries_df: pandas dataframe with the dataseries information
    """
    # generate a dataset
    dataset = generate_dataset(data_api, pumps_data_df,
                               pump_number, time_period, comment)
    # generate the dataseries related to this dataset
    generate_dataseries(data_api, dataset, dataseries_df)
    # get the dataseries IDs
    dataset.download_attributes()
    return dataset


def insert_dataset_pump_and_time(data_api, pump_number, time_period,
                                 time_period_start, time_period_end,
                                 comment, pumps_data_df, dataseries_df,
                                 datasets_df):
    """
    Insert a dataset ID in the datasets_df.
        :param data_api: instance of the class Data_API
        :param pump_number: pump numeric identifier
        :param time_period: time period in the format YYYYMM
        :param time_period_start: date in the format YYYY-MM-DD
        :param time_period_end: date in the format YYYY-MM-DD
        :param comment: comment to this dataset
        :param pumps_data_df: pandas dataframe with the pumps data
        :param dataseries_df: pandas dataframe with the dataseries information
        :param datasets_df: pandas dataframe with the data of each dataset
    """
    dt = generate_dataset_pump_and_time(data_api, pump_number, time_period,
                                        comment, pumps_data_df, dataseries_df)
    datasets_df.loc[len(datasets_df)] = {
        'id': dt.id,
        'timestamp':
        tm.get_timestamp_isoformat(),
        'pump_number': pump_number,
        'period': time_period,
        'period_start': time_period_start,
        'period_end': time_period_end,
        'comment': comment,
        }
    return datasets_df


def get_dataset_pump_and_time(pump_number, datasets_df, time_period=None):
    """
    Read out a dataset ID from datasets_df
        :param pump_number: pump numeric identifier
        :param time_period: time period in the format YYYYMM
        :param datasets_df: pandas dataframe with the data of each dataset
    """
    sb_df = datasets_df.loc[(datasets_df['pump_number'] == pump_number)]
    if time_period is not None:
        sb_df = sb_df.loc[(sb_df['period'] == time_period)]
    return sb_df.sort_values('timestamp', ascending=False)


def transfer_from_c8y_to_data_api(c8y, data_api, pump_number, time_period,
                                  pumps_data_df, dataseries_df,
                                  datasets_df, running_in_notebook=False):
    """
    Transfer data from a pump and a time period to the Data_API
        :param c8y: instance of the class c8y.Download
        :param data_api: instance of the class Data_API
        :param pump_number: pump numeric identifier
        :param time_period: time period in the format YYYYMM
        :param pumps_data_df: pandas dataframe with the pumps data
        :param dataseries_df: pandas dataframe with the dataseries information
        :param datasets_df: pandas dataframe with the data of each dataset
        :param dataset_id: optionally provide a dataset id
    """
    # get the most recent per default
    sub_df = get_dataset_pump_and_time(pump_number, datasets_df,
                                       time_period=time_period)
    dataset_id = sub_df.iloc[0].id
    date_from = sub_df.iloc[0].period_start
    date_to = sub_df.iloc[0].period_end

    dt = api.Dataset(data_api, id_=dataset_id)
    dt.download_attributes()
    # download from c8y
    # display a progress bar
    f = FloatProgress(min=0, max=dataseries_df.shape[0])
    if running_in_notebook:
        pass
        # display(f)
    for row in dataseries_df.itertuples():
        # download from c8y
        source = pumps_data_df.loc[pump_number]['c8y_id_' + str(row.c8y_id)]
        type_ = row.c8y_type
        measurements_df = c8y.download_values(date_from=date_from,
                                              date_to=date_to,
                                              source=source,
                                              type_=type_,
                                              to_datetime=False)
        # load to the data_api
        # get the right dataseries ID
        dataseries_id = dt.dataseries_ids[row.name]
        ds = api.Dataseries(dt, id_=dataseries_id)
        ds.upload_measurents_df(measurements_df)
        # update the progress bar
        f.value += 1
        if not running_in_notebook:
                print(f.value, ' of ', f.max)
