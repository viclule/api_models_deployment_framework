import base64
import requests
import json
import pandas as pd

import data_science.tools.transformations as tr


class Download:
    """
    Class to download data from the cumulocity platform.
    """

    def __init__(self, user, password,
                 url='http://leybold.cumulocity.com/measurement/measurements'):
        """
        Initialization function.
            :param self: self
            :param user: username in Cumulocity
            :param password: password in Cumulocity
            :param url: download url
        """
        self.download_path = url
        self.tenant = 'leybold'
        self.auth_base64 = self._authorization_base64(user, password)
        self.authorization = self._headers(self.auth_base64)

    def _authorization_base64(self, user, password):
        """
        Generate the authorizaiton string in base64.
            :param self: self
            :param user: username in Cumulocity
            :param password: password in Cumulocity
        """
        string = self.tenant + '/' + user + ':' + password
        return (b'Basic ' + base64.b64encode(string.encode('utf-8'))).decode()

    def _headers(self, authorization):
        """
        Return a dicitonary with the header information.
            :param self: self
            :param authorization: authorization string in base64
        """
        return {'Authorization': authorization}

    def _payload(self, date_to=None, date_from=None, source=None, type_=None):
        """
        Return the payload for measurements filtering.
            :param self: self
            :param date_to=None: date finishing at in the format YYYY-MM-DD
            :param date_from=None: date starting from in the format YYYY-MM-DD
            :param source=None: source ID
            :param type_=None: name of the measurement
        """
        payload = {'pageSize': 2000}
        if date_to is not None:
            payload['dateTo'] = date_to
        if date_from is not None:
            payload['dateFrom'] = date_from
        if source is not None:
            payload['source'] = source
        if type_ is not None:
            payload['type'] = type_
        return payload

    def download_values(self, date_to=None, date_from=None, source=None,
                        type_=None, to_datetime=True, remove_ms=True):
        """
        Download values from cumulocity.com.
            :param self: self
            :param date_to=None: date finishing at in the format YYYY-MM-DD
            :param date_from=None: date starting from in the format YYYY-MM-DD
            :param source=None: source ID
            :param type_=None: name of the measurement
            :param to_datetime=True: convert to datetime
            :param remove_ms=True: Remove the ms precision
        """
        df = pd.DataFrame(columns=('value', 'timestamp'))
        temp_dict = {'value': 'none', 'timestamp': 'none'}
        temp_do = True
        json_data = dict()
        payload_ = self._payload(date_to, date_from, source, type_)
        while temp_do or ('next' in json_data):
            if temp_do:
                r = requests.get(self.download_path,
                                 headers=self.authorization,
                                 params=payload_)
            else:
                r = requests.get(json_data['next'], headers=self.authorization)
            if r.status_code != 200:
                print("Status code: ", r.status_code)
                break
            json_data = json.loads(r.text)
            measurements = json_data['measurements']
            if len(measurements) == 0:
                break
            for measurement in measurements:
                try:
                    temp_dict['value'] = measurement[type_][type_]['value']
                except KeyError:
                    temp_dict['value'] = measurement[type_]['state']['value']

                if to_datetime:
                    temp_dict['timestamp'] = \
                        tr.iso_to_datetime(measurement['time'])
                else:
                    if remove_ms:
                        temp_dict['timestamp'] = measurement['time'][:-5] + 'Z'
                    else:
                        temp_dict['timestamp'] = measurement['time']
                df.loc[len(df)] = temp_dict
            temp_do = False
        return df
