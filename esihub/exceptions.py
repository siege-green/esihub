class ESIHubException(Exception):
    """Base exception for ESIHub"""


class ESIServerError(ESIHubException):
    """Raised when server returns an error"""


class ESIAuthenticationError(ESIHubException):
    """Raised when authentication fails"""


class ESIRateLimitExceeded(ESIHubException):
    """Raised when rate limit is exceeded"""


class ESIValidationError(ESIHubException):
    """Raised when data validation fails"""


class ESICacheError(ESIHubException):
    """Raised when there's an error with caching"""
