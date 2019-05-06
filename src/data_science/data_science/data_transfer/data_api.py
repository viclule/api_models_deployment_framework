import requests
import json
import pandas as pd
from ipywidgets import FloatProgress
import math

from data_science.tools.objects import attr_in_object, \
    assign_attr_from_dictionary
import data_science.tools.transformations as tr


class APIBaseClass:
    """
    Class with basic API interacting functionality.
    """
    _subpath = None

    def __init__(self):
        """Initialize the instance."""
        self._attr_to_dictionary = []
        self.links = {}

    def _fetch_json_from_url(self, request, expected_status_code,
                             field_to_fetch=None):
        """
        Fetchs a field from a request.
        """
        json_data = json.loads(request.text)
        if request.status_code != expected_status_code:
            error_message = f'API did not return {expected_status_code}. \
                              Status code: {request.status_code}.'
            if request.status_code == 403:
                raise Exception(error_message +
                                f"Message: {json_data['error']['code']}")
            raise Exception(error_message)
        if field_to_fetch is None:
            return json_data
        return json_data[field_to_fetch]

    def _generate_attr_to_dictionary(self):
        """
        Return a dictionary with the instance attributes specified in
        self.attr_to_dictionary
            :param self: self
        """
        dictionary = {}
        for attr in self._attr_to_dictionary:
            if getattr(self, attr) is not None:
                dictionary[attr] = getattr(self, attr)
        return dictionary

    def _assign_attributes(self, json_data):
        """
        Read data from a json object.
            :param self:
            :param json_data: a json object
        """
        for key, value in json_data.items():
            if (key != 'links') and (key != 'dataset'):
                assign_attr_from_dictionary(self, json_data, key)
            elif (key == 'links'):
                for value_ in value:
                    self.links[value_['rel']] = value_['href']
            elif (key == 'dataset'):
                    self.dataset = value['id']

    def generate_id(self):
        """
        Generate an id by communicating with the data_api.
            :param self: self
        """
        class_name = type(self).__name__.lower()
        self._verify_attr_completness(verify_id=False)
        path = self.data_api.api_url + self._subpath
        r = requests.post(path, headers=self.data_api.auth_header,
                          json=self._generate_attr_to_dictionary())
        json_data = self._fetch_json_from_url(r, 201)
        self._assign_attributes(json_data[class_name])
        if self.id is None:
            raise Exception('A ' + class_name +
                            ' id was not successfully generated')
        return self

    def upload_attributes(self):
        """
        Update the dataseries information in the Data_API.
            :param self:
        """
        self._verify_attr_completness()
        path = self.data_api.api_url + self._subpath + self.id
        r = requests.put(path, headers=self.data_api.auth_header,
                         json=self._generate_attr_to_dictionary())
        _ = self._fetch_json_from_url(r, 200)

    def download_attributes(self):
        """
        Collect the information from the Data_API.
            :param self:
        """
        class_name = type(self).__name__.lower()
        if self.id is None:
            raise AttributeError('A ' + class_name + ' id has to be provided.')
        path = self.data_api.api_url + self._subpath + self.id
        r = requests.get(path, headers=self.data_api.auth_header)
        json_data = self._fetch_json_from_url(r, 200)
        # extract the data from the respond
        self._assign_attributes(json_data[class_name])


class Dataseries(APIBaseClass):
    """
    Class representing a dataseries.
    """
    _subpath = '/dataseries/'

    def __init__(self, dataset_object, kind=None, pump_location=None,
                 name=None, units=None, precision=None,
                 id_=None, secondary_units=None, user=None,
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
        if (name is None) and (id_ is None):
            raise AttributeError('At least id or name has to be provided.')

        super().__init__()

        self.id = id_
        self._set_dataset(dataset_object)
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
        self._attr_to_dictionary = ['name', 'kind', 'pump_location', 'units',
                                    'precision', 'secondary_units',
                                    'dataset', 'numeric_identifier']
        self.data_to_measurement = ['value', 'secondary_value', 'frequency']
        self.MEASUREMENTS_PER_POST = 500
        self.df = pd.DataFrame()

    def _set_dataset(self, dataset_object):
        """
        Assign a Dataset object.
            :param self: self
            :param dataset_object: a Dataset instance
        """
        if not isinstance(dataset_object, Dataset):
            self.dataset = None
            raise TypeError('A dataset has to be provided.')
        self.dataset = dataset_object.id
        self.data_api = dataset_object.data_api

    def _verify_attr_completness(self, verify_id=True):
        """
        Verify that all required fields are provided.
        """
        if verify_id:
            if self.id is None:
                raise AttributeError('A dataset id has to be defined.')
        if self.dataset is None:
            raise AttributeError('A dataset object has to be provided.')
        if self.kind is None:
            raise AttributeError('A kind has to be provided.')
        if self.pump_location is None:
            raise AttributeError('A pump location has to be provided.')
        if self.units is None:
            raise AttributeError('Units has to be provided.')
        if self.precision is None:
            raise AttributeError('A precision has to be provided.')
        if self.name is None:
            raise AttributeError('A name has to be provided.')

    def _post_measurement(self, json_data):
        """
        Generate a request to post a measurement.
            :param self: self
            :param json_data: json object with the measurement information
        """
        if self.id is None:
            raise ValueError('A dataset id has to be provided.')
        path = self.data_api.api_url + __class__._subpath + self.id
        r = requests.post(path, headers=self.data_api.auth_header,
                          json=json_data)
        _ = self._fetch_json_from_url(r, 201)

    def upload_measurent(self, measurement):
        """
        Upload a measurement to the data_api.
            :param self: self
            :param measurement: Measurement instance
        """
        if not isinstance(measurement, Measurement):
            raise TypeError('A measurement has to be provided.')
        self._post_measurement(measurement.get_dictionary())

    def _upload_batch_measurents_df(self, measurements_df):
        """
        Send a df of measurements to the data_api.
            :param self: self
            :param measurements_df: dataframe with the measurements
        """
        data = []
        columns = measurements_df.columns
        for _, row in measurements_df.iterrows():
            measurement = Measurement(None)
            for column in columns:
                setattr(measurement, column, row[column])
            if measurement.value is not None:
                data.append(measurement.get_dictionary())
        self._post_measurement(data)

    def upload_measurents_df(self, measurements_df):
        """
        Send a batch of measurements one by one to the data_api.
            :param self: self
            :param measurements_df: dataframe with the measurements
        """
        length = measurements_df.shape[0]
        number_of_batches = math.ceil(length / self.MEASUREMENTS_PER_POST)
        for batch in range(number_of_batches):
            measurements = measurements_df[
                            (batch)*self.MEASUREMENTS_PER_POST:
                            (batch + 1)*self.MEASUREMENTS_PER_POST]
            self._upload_batch_measurents_df(measurements)

    def _get_measurements(self, path=None, from_time=None,
                          to_time=None):
        """
        Download measurements from the data_api.
            :param self: self
            :param path=None: path to the data_api
            :param from_time=None: starting from
            :param to_time=None: until
        """
        if self.id is None:
            raise ValueError('A dataset id has to be provided.')
        if path is None:
            path = self.data_api.api_url + __class__._subpath + self.id + \
                    '/measurements'
        else:
            path = self.data_api.api_url + path
        r = requests.get(path, headers=self.data_api.auth_header)
        json_data = self._fetch_json_from_url(r, 200)
        # extract the measurements and "next" link from the respond
        next_link = self._find_next(json_data['links'])
        return json_data['measurements'], next_link

    def get_measurements_df(self, from_time=None, to_time=None,
                            timestamp_to_datetime=False):
        """
        Download measurements from the data_api, returns a dataframe
            :param self: self
            :param path=None: path to the data_api
            :param from_time=None: starting from
            :param timestamp_to_datetime=False: convert to datetime if True
        """
        if self.id is None:
            raise ValueError('A dataset id has to be provided.')
        # create an empty dataframe
        df = Measurement(0).get_empty_df()
        # get the measurements
        next_link = None
        first = True
        while (next_link is not None) or first:
            first = False
            measurements, next_link = self._get_measurements(next_link,
                                                             from_time,
                                                             to_time)
            for measurement in measurements:
                if timestamp_to_datetime:
                    measurement['timestamp'] = \
                                tr.iso_to_datetime(measurement['timestamp'])
                df.loc[len(df)] = measurement
        return df

    def _find_next(self, links):
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


class Dataset(APIBaseClass):
    """
    Class representing a dataset.
    """
    _subpath = '/datasets/'

    def __init__(self, data_api, id_=None, name=None, pump_model=None,
                 kind=None, serial_number=None, other_identifier=None,
                 catalog_number=None, test_result=None,
                 test_result_comment=None, timestamp=None,
                 user=None, number_of_dataseries=None, description=None,):
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
        if (name is None) and (id_ is None):
            raise AttributeError('At least id or name has to be provided.')

        super().__init__()

        self.data_api = data_api
        self.id = id_
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
        self._attr_to_dictionary = ['name', 'pump_model', 'kind',
                                    'description',
                                    'serial_number',
                                    'other_identifier',
                                    'catalog_number']

    def _verify_attr_completness(self, verify_id=True):
        """
        Verify that all required fields are provided.
        """
        if verify_id:
            if self.id is None:
                raise AttributeError('A dataset id has to be defined.')
        if self.name is None:
            raise AttributeError('A name has to be provided.')
        if self.pump_model is None:
            raise AttributeError('A pump_model has to be provided.')
        if self.kind is None:
            raise AttributeError('A kind has to be provided.')
        if self.description is None:
            raise AttributeError('A description has to be provided.')
        if self.serial_number is None:
            raise AttributeError('A serial number has to be provided.')
        if self.catalog_number is None:
            raise AttributeError('A catalog number has to be provided.')

    def download_attributes(self):
        """
        Collect the dataset information in the Data_API.
            :param self:
        """
        super().download_attributes()
        # collect the related datseries
        self.get_list_of_dataseries()

    def get_list_of_dataseries(self):
        """
        Return a list with all the related dataseries to this dataset.
            :param self: self
        """
        path = self.data_api.api_url + __class__._subpath + self.id + \
            '/dataseries/'
        r = requests.get(path, headers=self.data_api.auth_header)
        json_data = self._fetch_json_from_url(r, 200)
        # extract the dataseries data from the respond
        self.dataseries_ids = {}
        for dataseries in json_data['dataseries']:
            self.dataseries_ids[dataseries['name']] = dataseries['id']
        return self.dataseries_ids

    def get_all_measurements_df(self, include_frequency=False,
                                include_secondary_value=False,
                                from_time=None, to_time=None,
                                timestamp_to_datetime=False,
                                running_in_notebook=False):
        """
        Download all the measurements from the dataseries.
            :param self: self
            :param include_frequency=False: frequency too if True
            :param include_secondary_value=False: secondary_value too if True
            :param timestamp_to_datetime=False: convert to datetime if True
        """
        df = pd.DataFrame()
        # display a progress bar
        f = FloatProgress(min=0, max=len(self.dataseries_ids))
        if running_in_notebook:
            # display(f)
            pass
        for _, id_ in self.dataseries_ids.items():
            ds = Dataseries(self, id_=id_)
            ds.download_attributes()
            df_temp = ds.get_measurements_df(from_time=from_time,
                to_time=to_time, timestamp_to_datetime=timestamp_to_datetime)
            # verify the size of the dataframe and resize dt if necessary
            if df_temp.shape[0] > df.shape[0]:
                diff = df_temp.shape[0] - df.shape[0]
                empty_df = pd.DataFrame(None,
                                        index=list(range(diff)),
                                        columns=df.columns)
                df = df.append(empty_df)
                df = df.reset_index(drop=True)
            # insert current dataseries measurements to df
            df[ds.name] = df_temp['value']
            df[ds.name + '_ts'] = df_temp['timestamp']
            if include_frequency:
                df[ds.name + '_fq'] = df_temp['frequency']
            if include_secondary_value:
                df[ds.name + '_sv'] = df_temp['secondary_value']
            # update the progress bar
            f.value += 1
            if not running_in_notebook:
                print(f.value, ' of ', f.max)
        return df

    def dump_attributes_to_dictionary(self):
        # ToDo: Probably add some more attributes
        return self._generate_attr_to_dictionary()


class DataApi(APIBaseClass):
    """
    Class representing the data_api.
    """
    _subpath = 'users/access_token/'

    def __init__(self, user, password, api_url, name='data_api'):
        """
        Initialization function.
            :param self: self
            :param user: user name
            :param password: user password
            :param api_url: api url
        """
        super().__init__()
        self.api_url = api_url
        self.user = user
        self.password = password
        self._headers()

    def _payload_token(self):
        """
        Return a dictionary to generate a token.
            :param self: self
        """
        return {'user_id': self.user,
                'user_secret': self.password}

    def _headers(self):
        """
        Generate an authorization header.
            :param self: self
        """
        self.auth_header = {'X-USER-ID': self.user,
                            'X-USER-TOKEN': self.get_token()}

    def get_token(self):
        """
        Get a new token from the data_api.
            :param self: self
        """
        path = self.api_url + __class__._subpath
        r = requests.post(path, json=self._payload_token())
        return self._fetch_json_from_url(r, 200, field_to_fetch='token')


class Measurement:
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

    def get_dictionary(self):
        """
        Return a dictionary with the measurement data.
            :param self: self
        """
        dictionary = {}
        members = attr_in_object(self)
        for member in members:
            if getattr(self, member) is not None:
                dictionary[member] = getattr(self, member)
        return dictionary

    def get_empty_df(self):
        """
        Return an empty dataframe with defined columns.
            :param self: self
        """
        columns = attr_in_object(self)
        return pd.DataFrame(columns=columns)
