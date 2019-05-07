import unittest

from data_science.tools.transformations import per_hour_to_per_second
#from ...tools.transformations import per_hour_to_per_second


class TransformationsTest(unittest.TestCase):
    """Test that the functions in transformations work as expected"""

    def test_per_hour_to_per_second(self):
        self.assertEqual(per_hour_to_per_second(3600), 1)
