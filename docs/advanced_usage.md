# Advanced Usage

This guide covers advanced features and usage patterns for ESIHub.

## Caching

ESIHub uses Redis for caching API responses. You can configure the Redis URL in your environment:

```bash
export ESI_REDIS_URL=redis://localhost:6379
```

The cache is used automatically for all requests. If a cached response is available and not expired, it will be returned instead of making a new API request.

## Rate Limiting

ESIHub implements automatic rate limiting to comply with EVE Online's API guidelines. The rate limiter ensures that your application doesn't exceed the allowed number of requests per second.

You can customize the rate limit:

```python
from esihub.core.rate_limiter import ESIRateLimiter

custom_rate_limiter = ESIRateLimiter(rate=100, per=1.0)
client = ESIHubClient(..., rate_limiter=custom_rate_limiter)
```

## Event System

ESIHub provides an event system that allows you to hook into the request lifecycle:

```python
@client.event_system.on('before_request')
def on_before_request(**kwargs):
    print(f"About to make a request: {kwargs['method']} {kwargs['path']}")

@client.event_system.on('after_request')
def on_after_request(**kwargs):
    print(f"Request completed: {kwargs['method']} {kwargs['path']}")
```

## Batch Requests

You can make multiple requests concurrently using the batch_request method:

```python
results = await client.batch_request([
    {"method": "GET", "path": "/characters/123/"},
    {"method": "GET", "path": "/corporations/456/"}
])
```

## Custom Session Management

For more control over the aiohttp ClientSession:

```python
from esihub.core.connection_pool import ESIConnectionPool

custom_pool = ESIConnectionPool(pool_size=200)
client = ESIHubClient(..., connection_pool=custom_pool)
```

## Logging

ESIHub uses Python's built-in logging module. You can configure the log level:

```python
import logging
logging.getLogger('esihub').setLevel(logging.DEBUG)
```

These advanced features allow you to fine-tune ESIHub's behavior to meet your application's specific needs.