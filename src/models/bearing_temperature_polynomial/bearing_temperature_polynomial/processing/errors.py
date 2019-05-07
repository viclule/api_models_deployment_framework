"""Custom defined errors for the data preprocessing"""


class BaseError(Exception):
    """Base package error."""
    pass


class InvalidModelInputError(BaseError):
    """Model input contains an error."""
    pass
