import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest

# from tests.test_data_transfer import DataTransferTest
from tests.tools.test_transformations import TransformationsTest


if __name__ == '__main__':
    unittest.main()
