# Error Handling

ESIHub provides custom exceptions to help you handle different types of errors that may occur when interacting with the ESI API.

## Exception Hierarchy

- `ESIHubException`: Base exception for all ESIHub errors
  - `ESIServerError`: Raised when the server returns an error (5xx status codes)
  - `ESIAuthenticationError`: Raised when authentication fails (401, 403 status codes)
  - `ESIRateLimitExceeded`: Raised when the rate limit is exceeded (429 status code)
  - `ESIValidationError`: Raised when data validation fails
  - `ESICacheError`: Raised when there's an error with caching

## Handling Exceptions

Here's an example of how to handle these exceptions:

```python
from esihub import ESIHubClient
from esihub.exceptions import (
    ESIHubException,
    ESIServerError,
    ESIAuthenticationError,
    ESIRateLimitExceeded
)

client = ESIHubClient(...)

try:
    character_info = await client.get_characters_character_id(character_id=12345)
except ESIServerError as e:
    print(f"Server error occurred: {e}")
except ESIAuthenticationError as e:
    print(f"Authentication failed: {e}")
except ESIRateLimitExceeded as e:
    print(f"Rate limit exceeded: {e}")
except ESIHubException as e:
    print(f"An error occurred: {e}")
```

## Automatic Retries

ESIHub automatically retries requests that fail due to rate limiting or temporary server errors. You can customize this behavior:

```python
from esihub.core.error_handler import ESIErrorHandler

custom_error_handler = ESIErrorHandler(max_retries=5, base_delay=1.0)
client = ESIHubClient(..., error_handler=custom_error_handler)
```

By properly handling these exceptions, you can make your application more robust and responsive to various error conditions.