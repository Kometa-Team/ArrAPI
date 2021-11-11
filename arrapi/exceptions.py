class ArrException(Exception):
    """ Base class for all ArrAPI exceptions. """
    pass


class ConnectionFailure(ArrException):
    """ Failed to connect to Arr instance. """
    pass


class Excluded(ArrException):
    """ Item is excluded from being added to the Arr instance. """
    pass


class Exists(ArrException):
    """ Item already exists in the Arr instance. """
    pass


class Invalid(ArrException):
    """ Invalid Selection. """
    pass


class NotFound(ArrException):
    """ Item not found. """
    pass


class Unauthorized(ArrException):
    """ Invalid apikey. """
    pass
