class ESIHubError(Exception):
    def __init__(self, message: str, status_code: int = None, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ESIHubAuthenticationError(ESIHubError):
    pass


class ESIHubRateLimitError(ESIHubError):
    pass


class ESIHubServerError(ESIHubError):
    pass


class ESIHubClientError(ESIHubError):
    pass


class ESIHubValidationError(ESIHubError):
    pass
