"""Aries exceptions. All exceptions in aries project are define here."""


class AriesException(Exception):
    """Base exception for aries project"""


class SimulationError(AriesException):
    """Raised when something goes wrong in simulation itself
    """


class FilePathNotFoundError(AriesException):
    """Raised if config file or relaed files not found
    """


class ValidationError(AriesException):
    """Raised in case validation of json format is not passed
    """
