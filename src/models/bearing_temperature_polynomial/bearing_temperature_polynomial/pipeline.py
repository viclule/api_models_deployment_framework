from sklearn.linear_model import Lasso
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.preprocessing import StandardScaler

# from bearing_temperature_polynomial.processing import preprocessors as pp
from bearing_temperature_polynomial.processing import features
from bearing_temperature_polynomial.config import config

import logging


_logger = logging.getLogger(__name__)


model_pipe = Pipeline(
    [
        ('log_transformer',
            features.LogTransformer(variables=config.NUMERICALS_LOG_VARS)),
        ('scl',
            StandardScaler()),
        ('poly_features',
            PolynomialFeatures(degree=config.POLYNOMIAL_DEGREE)),
        ('lasso',
            Lasso(alpha=config.LASSO_ALPHA)),
    ]
)
