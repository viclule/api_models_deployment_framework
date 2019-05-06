import os
import sys
import unittest

# from tests.test_data_transfer import DataTransferTest
from tools.test_transformations import TransformationsTest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


if __name__ == '__main__':
    unittest.main()
