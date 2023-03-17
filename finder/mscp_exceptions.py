"""
File that contains the exceptions that can be raised during the execution of the main loop of the MSCP algorithm
"""


class ImpossibleModelChangeException(Exception):
    """
    The model change that predates a test can not be built because the instance does not mathematically allow it
    """
    pass


class OperatorDisabledException(Exception):
    """
    The operator that we try to access is disabled
    """
    pass
