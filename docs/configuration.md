# Configuration

ESIHub can be configured using environment variables or programmatically.

## Environment Variables

- `ESI_CLIENT_ID`: Your EVE Online application's client ID
- `ESI_CLIENT_SECRET`: Your EVE Online application's client secret
- `ESI_CALLBACK_URL`: The callback URL for your application
- `ESI_BASE_URL`: The base URL for the ESI API (default: "https://esi.evetech.net")
- `ESI_REDIS_URL`: The URL for your Redis instance (default: "redis://localhost:6379")
- `ESI_LOG_LEVEL`: The logging level (default: "INFO")

Example:

```bash
export ESI_CLIENT_ID=your_client_id
export ESI_CLIENT_SECRET=your_client_secret
export ESI_CALLBACK_URL=http://localhost:8000/callback
export ESI_REDIS_URL=redis://localhost:6379
export ESI_LOG_LEVEL=DEBUG
```

## Programmatic Configuration

You can also configure ESIHub programmatically when initializing the client:

```python
from esihub import ESIHubClient
from esihub.core.cache import ESICache
from esihub.core.rate_limiter import ESIRateLimiter

client = ESIHubClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    callback_url="your_callback_url",
    base_url="https://esi.evetech.net",
    cache=ESICache(redis_url="redis://localhost:6379"),
    rate_limiter=ESIRateLimiter(rate=150, per=1.0)
)
```

This approach allows for more fine-grained control over the client's behavior.

Remember to keep your client ID and secret secure, and never commit them to version control.