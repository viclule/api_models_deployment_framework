# Functionality to read and store in HDF5 files
import h5py
import pandas as pd
import random
import string
import os
import datetime
import json

from data_science.data_transfer.data_api import Dataset


class HDF5Dataset:

    def __init__(self, file_name, file_path, dataset_id,
                 random_string_in_name=10):
        """
        Initialization.
            :param self:
            :param file_name: name for the file. No ending necessary
            :param file_path: location path
            :param dataset_id: dataset's id
            :param random_string_in_name: lenght of the random string to add to
                                            the name
        """
        self.file_name = file_name
        self.file_path = file_path
        self.file_w_path = os.path.join(self.file_path, self.file_name)
        self._dataset_id = dataset_id
        self.random_string_in_name = random_string_in_name

    @property
    def dataset_id(self):
        # do something
        return self._dataset_id

    @dataset_id.setter
    def dataset_id(self, value):
        self._dataset_id = value

    def create_h5_file(self):
        """
        Create the h5 file and add the groups.
            :param self: self
        """
        self.file_name = self.file_name + '-' + \
            _generate_random_string(l=self.random_string_in_name) + '.h5'
        self.file_w_path = os.path.join(self.file_path, self.file_name)
        try:
            f = h5py.File(self.file_w_path, 'a')
            f.create_group('meta')
            f.create_group('meta/columns')
            f.create_group('data')
            f.close()
            return self.file_name
        except ValueError as e:
            print(e)
            return

    def add_dataset_meta_to_h5(self, dataset):
        """
        Add the meta data of the dataset to the file. Consist of:
        A dataframe with the dataset attributes.
        A dataframe with the columns of the dataset.
            :param self: self
            :param dataset: a Dataset instance
        """
        if not isinstance(dataset, Dataset):
            raise TypeError('A dataset has to be provided.')
        # create a df with the metadata
        columns = list(dataset.dump_attributes_to_dictionary().keys())
        df = pd.DataFrame(columns=columns)
        df.loc[0] = dataset.dump_attributes_to_dictionary()
        # insert to the file
        df.to_hdf(self.file_w_path, key='meta/' + self._dataset_id, mode='a')

    def add_dataset_data_df_to_h5(self, df):
        """
        Add the data of the dataset to the file.
            :param self: self
            :param df: dataframe with the data
        """
        # insert the df to the file
        df.to_hdf(self.file_name, key='data/' + self._dataset_id, mode='a')
        # insert the columns names as df to the metadata
        df_col = pd.DataFrame(columns=['columns'])
        df_col['columns'] = list(df.columns.values)
        # insert to the file
        df_col.to_hdf(self.file_w_path,
                      key='meta/columns/' + self._dataset_id,
                      mode='a')

    def remove_dataset_from_h5(self):
        """
        Remove the dataset from the file.
            :param self: self
        """
        try:
            with h5py.File(self.file_w_path, 'a') as f:
                del f['data/' + self._dataset_id]
                del f['meta/' + self._dataset_id]
                del f['meta/columns/' + self._dataset_id]
        except KeyError as e:
            print(e)

    def read_dataset_data_df_from_h5(self):
        """
        Read the data from the file. Returns a dataframe.
            :param self: self
        """
        try:
            df = pd.read_hdf(self.file_w_path, 'data/' + self._dataset_id, 'r')
            return df
        except KeyError as e:
            print(e)

    def read_dataset_meta_df_from_h5(self):
        """
        Read the meta data from the file. Returns a dataframe.
            :param self: self
        """
        try:
            df = pd.read_hdf(self.file_w_path, 'meta/' + self._dataset_id, 'r')
            return df
        except KeyError as e:
            print(e)

    def get_column_names_from_h5(self):
        """
        Get the column names from the file. Returns a dataframe.
            :param self: self
        """
        try:
            df = pd.read_hdf(self.file_w_path,
                             'meta/columns/' + self._dataset_id, 'r')
            return df
        except KeyError as e:
            print(e)

    def get_keys(self, option='data'):
        """
        Get a list with the dataset_id's stored in the file.
            :param self: self
            :param option='data': Read the keys from the 'data', 'meta' or
            'meta/columns/' group.
        """
        keys = None
        try:
            with h5py.File(self.file_w_path, 'r') as f:
                keys = [key for key in f[option].keys()]
            if 'columns' in keys:
                keys.remove('columns')
            return keys
        except KeyError as e:
            print(e)


def _generate_random_string(l=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=l))


def generate_hd5f_from_df(df, file_name, file_path, datasets=[],
                          random_string_in_name=10):
    """
    Generates an hdf5 file from a DataFrame.
            :param self:
            :param file_name: name for the file. No ending necessary
            :param file_path: location path
            :param datasets: array with the dataset ids used to build the df
            :param random_string_in_name: lenght of the random string to add to
                                            the name
    """
    file_name = file_name + '-' + \
        _generate_random_string(l=random_string_in_name) + '.h5'
    file_w_path = os.path.join(file_path, file_name)
    try:
        with h5py.File(file_w_path, 'a') as f:
            g = f.create_group('base_group')
            g.create_dataset('metadata', data=json.dumps({}))
    except ValueError as e:
        print(e)
        return
    # Generate the metadata
    metadata = {'date': datetime.datetime.now().isoformat(),
                'datasets': datasets,
                'columns': list(df.columns.values)}
    # Insert the metadata and the array
    with h5py.File(file_w_path, 'a') as f:
        f['base_group/metadata'][()] = json.dumps(metadata)
        _ = f.create_dataset('base_group/data', data=df.reset_index().values)
    return file_name


def generate_df_from_hdf5(file_name):
    """
    Generates a DataFrame from a dataframe.
            :param file_name: name with path of the hdf5 file
    """
    try:
        with h5py.File(file_name, 'a') as f:
            data = f['base_group/data'][:]
            metadata = json.loads(f['base_group/metadata'][()])
    except ValueError as e:
        print(e)
        return
    lt = ['index']
    lt.extend(metadata['columns'])
    df = pd.DataFrame(data, columns=lt)
    df = df.set_index('index')
    datasets = metadata['datasets']
    return df, datasets
