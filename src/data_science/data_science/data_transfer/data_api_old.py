import requests
import json
import pandas as pd
import math
import numpy as np
from ipywidgets import FloatProgress

import data_science.tools.json as js
import data_science.tools.transformations as tr


class Dataseries():
    """
    Class representing a dataseries.
    """
    def __init__(self, dataset_object, kind=None, pump_location=None,
                 name=None, units=None, precision=None,
                 id=None, secondary_units=None, user=None,
                 number_of_measurements=None, timestamp=None,
                 numeric_identifier=None,):
        """
        Initialization function.
            :param self: self
            :param dataset_object: a Dataset object, parent of the dataseries
            :param kind=None: kind of measurement. temperature, pressure, etc.
            :param pump_location=None: location in the pump, inlet,
                                        outlet, motor, etc.
            :param name=None: name for the dataseries
            :param units=None: units of the measurement
            :param precision=None: precision of the sensor used
            :param numeric_identifier=None: a numeric identifier
            :param id=None: id provided by the data_api
            :param secondary_units=None: units for the secondary value
            :param user=None: creator of the dataseries
            :param number_of_measurements=None: number of measurements already
                                                excistant in the data_api
            :param timestamp=None: time of creation
        """
        self.id = id
        self.dataset_object = dataset_object
        self.kind = kind
        self.pump_location = pump_location
        self.name = name
        self.units = units
        self.precision = precision
        self.numeric_identifier = numeric_identifier
        self.secondary_units = secondary_units
        self.user_id = user
        self.number_of_measurements = number_of_measurements
        self.timestamp = timestamp
        self.links = {}
        self.subpath = '/dataseries/'
        self.data_to_post = ['name', 'kind', 'pump_location', 'units',
                            'precision', 'secondary_units', 'dataset',
                            'numeric_identifier']
        self.data_to_measurement = ['value', 'secondary_value', 'frequency']
        self.set_dataset(self.dataset_object)
        self.MEASUREMENTS_PER_POST = 500

    def set_dataset(self, dataset_object):
        """
        Assign a Dataset object.
            :param self: self
            :param dataset_object: a Dataset instance
        """
        if not isinstance(dataset_object, Dataset):
            self.dataset = None
            raise TypeError('A dataset has to be provided.')
        self.dataset = dataset_object.id

    def read_from_json(self, json_data):
        """
        Read data from a json object.
            :param self: 
            :param json_data: a json object
        """
        for key, value in json_data.items():
            if (key != 'links') and (key != 'dataset'):
                js.read_from_json(self, json_data, key)
            elif key == 'links':
                for value_ in value:
                    self.links[value_['rel']] = value_['href']
            elif key == 'dataset':
                self.dataset = value['id']

    def data_dataseries(self):
        """
        Return a dictionary with the dataseries data.
            :param self: self
        """
        dataseries = {}
        for data in self.data_to_post:
            if getattr(self, data) is not None:
                dataseries[data] = getattr(self, data)
        return dataseries

    def verify_completness(self, verify_id=True):
        """
        Verify the necessary information is available to communicate with the
        data_api.
            :param self: self
            :param verify_id=True: True to verify id precense too
        """
        if verify_id:
            if self.id is None:
                raise ValueError('A dataseries id has to be provided.')
        if self.dataset_object is None:
            raise ValueError('A dataset_object has to be provided.')
        if self.kind is None:
            raise ValueError('A kind has to be provided.')
        if self.pump_location is None:
            raise ValueError('A pump_location has to be provided.')
        if self.name is None:
            raise ValueError('A name has to be provided.')
        if self.units is None:
            raise ValueError('A unit has to be provided.')
        if self.precision is None:
            raise ValueError('A precision has to be provided.')

    def generate_id(self, data_api):
        """
        Generate an id by communicating with the data_api.
            :param self: self
            :param data_api: Data_API instance
        """
        self.verify_completness(verify_id=False)
        path = data_api.URL + self.subpath
        r = requests.post(path, headers=data_api.auth_header,
                          json=self.data_dataseries())
        if r.status_code != 201:
            raise Exception('data_api did not return 201. Status code: ' + \
                            str(r.status_code))
        json_data = json.loads(r.text)
        self.read_from_json(json_data['dataseries'])
        return self.id

    def update_info(self, data_api):
        """
        Update the dataseries information in the Data_API.
            :param self: 
            :param data_api: Data_API instance
        """
        self.verify_completness()
        path = data_api.URL + self.subpath + self.id
        r = requests.put(path, headers=data_api.auth_header,
                         json=self.data_dataseries())
        if r.status_code != 200:
            raise Exception('data_api did not return 200. Status code: ' + \
                            str(r.status_code))
        json_data = json.loads(r.text)
        # extract the dataset data from the respond
        self.read_from_json(json_data['dataseries'])

    def get_info(self, data_api):
        """
        Collect the dataseries information in the Data_API.
            :param self: 
            :param data_api: Data_API instance
        """
        if self.id is None:
            raise ValueError('A dataset id has to be provided.')
        path = data_api.URL + self.subpath + self.id
        r = requests.get(path, headers=data_api.auth_header)
        if r.status_code != 200:
            raise Exception('data_api did not return 200. Status code: ' + \
                            str(r.status_code))
        json_data = json.loads(r.text)
        # extract the dataseries data from the respond
        self.read_from_json(json_data['dataseries'])

    def post_measurement_request(self, data_api, json_data):
        """
        Generate a request to post a measurement.
            :param self: self
            :param data_api: Data_API instance
            :param json_data: json object with the measurement information
        """
        if self.id is None:
            raise ValueError('A dataset id has to be provided.')
        path = data_api.URL + self.subpath + self.id
        r = requests.post(path, headers=data_api.auth_header,
                          json=json_data)
        if r.status_code != 201:
            raise Exception('data_api did not return 201. Status code: ' + \
                            str(r.status_code))

    def post_measurement(self, data_api, value, secondary_value=None,
                         frequency=None, timestamp=None):
        """
        Send a measurement to the data_api.
            :param self: self
            :param data_api: Data_API instance
            :param value: value
            :param secondary_value=None: secondary_value
            :param frequency=None: frequency
            :param timestamp=None: timestamp
        """
        measurement = Measurement(value, secondary_value, frequency, timestamp)
        self.post_measurement_request(data_api,
                                      [measurement.data_measurement()])

    def post_batch_measurements_df(self, data_api, measurements_df):
        """
        Send a batch of measurements to the data_api.
            :param self: self
            :param data_api: Data_API instance
            :param measurements_df: dataframe with the measurements
        """
        data = []
        for measurement in measurements_df.itertuples():
            value = measurement.value
            timestamp = None
            secondary_value = None
            frequency = None
            try:
                secondary_value = measurement.secondary_value
            except:
                pass
            try:
                frequency = measurement.frequency
            except:
                pass
            try:
                timestamp = measurement.timestamp
            except:
                pass
            measurement = Measurement(value, secondary_value, frequency,
                                      timestamp)
            data.append(measurement.data_measurement())
        self.post_measurement_request(data_api, data)

    def post_measurements_df(self, data_api, measurements_df):
        """
        Send a batch of measurements one by one to the data_api.
            :param self: self
            :param data_api: Data_API instance
            :param measurements_df: dataframe with the measurements
        """
        length = measurements_df.shape[0]
        number_of_batches = math.ceil(length / self.MEASUREMENTS_PER_POST)
        for batch in range(number_of_batches):
            measurements = measurements_df[
                            (batch)*self.MEASUREMENTS_PER_POST: \
                            (batch + 1)*self.MEASUREMENTS_PER_POST]
            self.post_batch_measurements_df(data_api, measurements)

    def get_measurements(self, data_api, path=None, from_time=None,
                         to_time=None):
        """
        Download measurements from the data_api.
            :param self: self
            :param data_api: Data_API instance
            :param path=None: path to the data_api
            :param from_time=None: starting from
            :param to_time=None: until
        """
        if self.id is None:
            raise ValueError('A dataset id has to be provided.')
        if path is None:
            path = data_api.URL + self.subpath + self.id + '/measurements'
        else:
            path = data_api.URL + path
        r = requests.get(path, headers=data_api.auth_header)
        if r.status_code != 200:
            raise Exception('data_api did not return 200. Status code: ' + \
                            str(r.status_code))
        json_data = json.loads(r.text)
        # extract the measurements and "next" link from the respond
        next_link = self.find_next(json_data['links'])
        return json_data['measurements'], next_link

    def get_measurements_df(self, data_api, from_time=None, to_time=None,
                            timestamp_to_datetime=False):
        """
        Download measurements from the data_api, returns a dataframe
            :param self: self
            :param data_api: Data_API instance
            :param path=None: path to the data_api
            :param from_time=None: starting from
            :param timestamp_to_datetime=False: convert to datetime if True
        """
        if self.id is None:
            raise ValueError('A dataset id has to be provided.')
        # create an empty dataframe
        df = Measurement(0).empty_dataframe()
        # get the measurements
        next_link = None
        first = True
        while (next_link is not None) or first:
            first = False
            measurements, next_link = self.get_measurements(data_api,
                                                            next_link,
                                                            from_time,
                                                            to_time)
            for measurement in measurements:
                if timestamp_to_datetime:
                    measurement['timestamp'] = \
                                tr.iso_to_datetime(measurement['timestamp'])
                df.loc[len(df)] = measurement
        return df

    def get_full_dataseries(self, data_api, from_time=None, to_time=None,
                            timestamp_to_datetime=False):
        # load the measurements
        df = self.get_measurements_df(data_api, from_time, to_time,
                                      timestamp_to_datetime)
        # add the rest of relevant information
        df['dataset_id'] = self.dataset_object.id
        df['dataset_name'] = self.dataset_object.name
        df['dataseries_id'] = self.id
        df['dataseries_name'] = self.name
        return df

    def find_next(self, links):
        """
        Find the next link in the json object.
            :param self: 
            :param links: links
        """
        found = False
        next_link = None
        for link in links:
            for _, value in link.items():
                if value == 'next':
                    found = True
            if found:
                next_link = link['href']
                break
        return next_link


class Dataset():
    """
    Class representing a dataset.
    """
    def __init__(self, name=None, pump_model=None, kind=None, description=None,
                 serial_number=None, other_identifier=None, catalog_number=None,
                 test_result=None, test_result_comment=None, timestamp=None,
                 user=None, number_of_dataseries=None, id=None,):
        """
        Initialization function.
            :param self: self
            :param name=None: name for the dataset 
            :param pump_model=None: pump model
            :param kind=None: kind of dataset
            :param description=None: description
            :param serial_number=None: serial number
            :param other_identifier=None: another identifier
            :param catalog_number=None: catalog number
            :param test_result=None: test result if it is a test
            :param test_result_comment=None: test result comment
            :param timestamp=None: time
            :param user=None: user creator of the dataset
            :param number_of_dataseries=None: number of dataseries related
            :param id=None: id provided by the data_api
        """
        self.id = id
        self.name = name
        self.pump_model = pump_model
        self.kind = kind
        self.description = description
        self.serial_number = serial_number
        self.other_identifier = other_identifier
        self.catalog_number = catalog_number
        self.test_result = test_result
        self.test_result_comment = test_result_comment
        self.timestamp = timestamp
        self.user_id = user
        self.number_of_dataseries = number_of_dataseries
        self.dataseries_ids = {}
        self.links = {}
        self.subpath = '/datasets/'
        self.data_to_post = ['name', 'pump_model', 'kind', 'description',
                             'serial_number', 'other_identifier',
                             'catalog_number']

    def read_from_json(self, json_data):
        """
        Read data from a json object.
            :param self: 
            :param json_data: a json object
        """
        for key, value in json_data.items():
            if key != 'links':
                js.read_from_json(self, json_data, key)
            else:
                for value_ in value:
                    self.links[value_['rel']] = value_['href']

    def data_dataset(self):
        """
        Return a dictionary with the dataset data.
            :param self: self
        """
        dataset = {}
        for data in self.data_to_post:
            if getattr(self, data) is not None:
                dataset[data] = getattr(self, data)
        return dataset

    def generate_id(self, data_api):
        """
        Generate an id by communicating with the data_api.
            :param self: self
            :param data_api: Data_API instance
        """
        path = data_api.URL + self.subpath
        r = requests.post(path, headers=data_api.auth_header,
                          json=self.data_dataset())
        if r.status_code != 201:
            raise Exception('data_api did not return 201. Status code: ' + \
                            str(r.status_code))
        json_data = json.loads(r.text)
        self.read_from_json(json_data['dataset'])
        if self.id is None:
            raise Exception('A dataset id was not successfully generated')
        return self

    def update_info(self, data_api):
        """
        Update the dataset information in the Data_API.
            :param self: 
            :param data_api: Data_API instance
        """
        if self.id is None:
            raise ValueError('A dataset id has to be provided.')
        if self.name is None:
            raise ValueError('A name has to be provided.')
        if self.pump_model is None:
            raise ValueError('A pump_model has to be provided.')
        if self.kind is None:
            raise ValueError('A kind has to be provided.')
        if self.description is None:
            raise ValueError('A description has to be provided.')
        path = data_api.URL + self.subpath + self.id
        r = requests.put(path, headers=data_api.auth_header,
                         json=self.data_dataset())
        if r.status_code != 200:
            raise Exception('data_api did not return 200. Status code: ' + \
                            str(r.status_code))
        json_data = json.loads(r.text)
        # extract the dataset data from the respond
        self.read_from_json(json_data['dataset'])

    def get_info(self, data_api):
        """
        Collect the dataset information in the Data_API.
            :param self: 
            :param data_api: Data_API instance
        """
        if self.id is None:
            raise ValueError('A dataset id has to be provided.')
        path = data_api.URL + self.subpath + self.id
        r = requests.get(path, headers=data_api.auth_header)
        if r.status_code != 200:
            raise Exception('data_api did not return 200. Status code: ' + \
                            str(r.status_code))
        json_data = json.loads(r.text)
        # extract the dataset data from the respond
        self.read_from_json(json_data['dataset'])
        # collect the related datseries
        self.get_list_of_dataseries(data_api)

    def get_list_of_dataseries(self, data_api):
        """
        Return a list with all the related dataseries to this dataset.
            :param self: self
            :param data_api: Data_API instance
        """
        path = data_api.URL + self.subpath + self.id + '/dataseries/'
        r = requests.get(path, headers=data_api.auth_header)
        if r.status_code != 200:
            raise Exception('data_api did not return 200. Status code: ' + \
                            str(r.status_code))
        json_data = json.loads(r.text)
        # extract the dataseries data from the respond
        self.dataseries_ids = {}
        for dataseries in json_data['dataseries']:
            self.dataseries_ids[dataseries['name']] = dataseries['id']

    def get_all_measurements_df(self, data_api, frequency=False,
                                secondary_value=False,
                                from_time=None, to_time=None,
                                timestamp_to_datetime=False):
        """
        Download all the measurements from the dataseries.
            :param self: self
            :param data_api: Data_API instance
            :param frequency=False: frequency too if True
            :param secondary_value=False: secondary_value too if True
            :param timestamp_to_datetime=False: convert to datetime if True
        """
        df = pd.DataFrame()
        # display a progress bar
        f = FloatProgress(min=0, max=len(self.dataseries_ids))
        display(f)
        for _, id_ in self.dataseries_ids.items():
            ds = Dataseries(self, id=id_)
            ds.get_info(data_api)
            df_temp = ds.get_measurements_df(data_api, from_time=from_time,
                                to_time=to_time,
                                timestamp_to_datetime=timestamp_to_datetime)
            # verify the size of the dataframe and resize dt if necessary
            if df_temp.shape[0] > df.shape[0]:
                diff = df_temp.shape[0] - df.shape[0]
                empty_df = pd.DataFrame(None,
                                        index=list(range(diff)),
                                        columns=df.columns)
                df = df.append(empty_df)
                df = df.reset_index()
            # insert current dataseries measurements to df
            df[ds.name] = df_temp['value']
            df[ds.name + '_ts'] = df_temp['timestamp']
            if frequency:
                df[ds.name + '_fq'] = df_temp['frequency']
            if secondary_value:
                df[ds.name + '_sv'] = df_temp['secondary_value']
            # update the progress bar
            f.value += 1
        return df


class Measurement():
    """
    Class representing a measurement.
    """

    def __init__(self, value, secondary_value=None,
                 frequency=None, timestamp=None):
        """
        Initialization function.
            :param self: self
            :param value: value
            :param secondary_value=None: secondary_value
            :param frequency=None: frequency
            :param timestamp=None: timestamp
        """
        self.value = value
        self.secondary_value = secondary_value
        self.frequency = frequency
        self.timestamp = timestamp

    def data_measurement(self):
        """
        Return a dictionary with the measurement data.
            :param self: self
        """
        measurement = {}
        members = js.attr_in_object(self)
        for member in members:
            if getattr(self, member) is not None:
                measurement[member] = getattr(self, member)
        return measurement

    def empty_dataframe(self):
        """
        Return an empty dataframe with defined columns.
            :param self: self
        """
        columns = js.attr_in_object(self)
        return pd.DataFrame(columns=columns)


class Data_API():
    """
    Class representing the data_api.
    """

    def __init__(self, user, password):
        """
        Initialization function.
            :param self: self
            :param user: user name
            :param password: user password
        """
        self.URL = 'http://159.65.23.102:8000/'
        self.user = user
        self.password = password
        self.get_authorization_header()

    def data_token(self):
        """
        Return a dictionary to generate a token.
            :param self: self
        """
        return {'user_id' : self.user,
                'user_secret' : self.password}

    def get_token(self):
        """
        Get a new token from the data_api.
            :param self: self
        """
        path = self.URL + 'users/access_token/'
        r = requests.post(path, json=self.data_token())
        json_data = json.loads(r.text)
        if r.status_code == 403:
            raise ValueError(json_data['error']['code'])
        self.token = json_data['token']
        return self.token

    def get_authorization_header(self):
        """
        Generate an authorization header.
            :param self: self
        """
        self.auth_header = {'X-USER-ID': self.user,
                            'X-USER-TOKEN': self.get_token()}
