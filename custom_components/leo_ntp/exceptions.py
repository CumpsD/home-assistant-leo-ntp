"""Exceptions used by LeoNTP."""


class LeoNTPException(Exception):
    """Base class for all exceptions raised by LeoNTP."""
    pass


class LeoNTPServiceException(Exception):
    """Raised when service is not available."""
    pass

class NotAuthenticatedException(Exception):
    """Raised when session is invalid."""
    pass


class GatewayTimeoutException(LeoNTPServiceException):
    """Raised when server times out."""
    pass


class BadGatewayException(LeoNTPServiceException):
    """Raised when server returns Bad Gateway."""
    pass
