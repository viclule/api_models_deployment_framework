import unittest

from data_science.data_transfer.data_api import Data_API, Dataset, Dataseries
from secret import PASSWORD_DATA_API, USERNAME_DATA_API


class DataTransferTest(unittest.TestCase):
    def test_get_access_data_api(self):
        data_API = Data_API(USERNAME_DATA_API,
                            PASSWORD_DATA_API)
        assert len(data_API.token) == 36

    def test_dataset(self):
        data_API = Data_API(USERNAME_DATA_API,
                            PASSWORD_DATA_API)

        dt = Dataset(name="unittest",
                     pump_model="unittest",
                     kind="unittest",
                     description="unittest")
        dt.generate_id(data_API)
        assert len(dt.id) == 36

    def test_dataseries(self):
        data_API = Data_API(USERNAME_DATA_API,
                            PASSWORD_DATA_API)

        dt = Dataset(name="unittest",
                     pump_model="unittest",
                     kind="unittest",
                     description="unittest")
        dt.generate_id(data_API)

        ds = Dataseries(dt,
                        kind="unittest",
                        pump_location="unittest",
                        name="unittest",
                        numeric_identifier=1,
                        units="unittest",
                        precision=12)
        ds.generate_id(data_API)
        assert len(ds.id) == 24

        ds.post_measurement(data_API, 101.12,
                            secondary_value=12,
                            frequency=13.1)

        ds.get_info(data_API)

        assert ds.number_of_measurements == 1
