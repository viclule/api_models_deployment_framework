import pathlib
import bearing_temperature_polynomial
import pandas as pd


pd.options.display.max_rows = 10
pd.options.display.max_columns = 10


PACKAGE_ROOT = pathlib.Path(
    bearing_temperature_polynomial.__file__).resolve().parent
TRAINED_MODEL_DIR = PACKAGE_ROOT / 'trained_models'
DATASET_DIR = PACKAGE_ROOT / 'datasets'

# data
TESTING_DATA_FILE = 'test.csv'
TRAINING_DATA_FILE = 'train.csv'
TARGET = 'bearing_motor_temperature_ew_9'


# variables
FEATURES = [
    'water_heat_removal_ew_9',
    'water_inlet_temperature_ew_9',
    'water_outlet_temperature_ew_9',
    'gas_inlet_pressure_ew_9',
    'gas_inlet_temperature_ew_9',
    'gas_outlet_temperature_ew_9',
    'inverter_power_ew_9',
]

# this variable is to calculate the temporal variable,
# can be dropped afterwards
DROP_FEATURES = []

# numerical variables with NA in train set
NUMERICAL_VARS_WITH_NA = []

# categorical variables with NA in train set
CATEGORICAL_VARS_WITH_NA = []

TEMPORAL_VARS = []

# variables to log transform
NUMERICALS_LOG_VARS = ['gas_inlet_pressure_ew_9']

# categorical variables to encode
CATEGORICAL_VARS = []

NUMERICAL_NA_NOT_ALLOWED = [
    feature for feature in FEATURES
    if feature not in CATEGORICAL_VARS + NUMERICAL_VARS_WITH_NA
]

CATEGORICAL_NA_NOT_ALLOWED = [
    feature for feature in CATEGORICAL_VARS
    if feature not in CATEGORICAL_VARS_WITH_NA
]

POLYNOMIAL_DEGREE = 3
LASSO_ALPHA = 0.005

PIPELINE_NAME = 'polynomial_regression'
PIPELINE_SAVE_FILE = f'{PIPELINE_NAME}_output_v'

# used for differential testing
ACCEPTABLE_MODEL_DIFFERENCE = 0.5


# Other configurations

# ramdom seed for sklearn, numpy and pandas
RANDOM_SEED = 0

# proportion of the dataset reserved for testing purposes
TEST_SIZE = 0.25
