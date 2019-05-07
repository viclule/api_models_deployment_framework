import unittest
#import sys, os
#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from data_science.tools.transformations import per_hour_to_per_second
#from ...tools.transformations import per_hour_to_per_second


class TransformationsTest(unittest.TestCase):
    """Test that the functions in transformations work as expected"""

    def test_per_hour_to_per_second(self):
        self.assertEqual(per_hour_to_per_second(3600), 1)
