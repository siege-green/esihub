# ESIHub Detailed Guide

## Table of Contents
1. [Installation](#installation)
2. [Client Initialization](#client-initialization)
3. [Making Requests](#making-requests)
4. [Pagination](#pagination)
5. [SSO (Single Sign-On)](#sso-single-sign-on)
6. [Caching](#caching)
7. [Rate Limiting](#rate-limiting)
8. [Error Handling](#error-handling)
9. [Telemetry and Monitoring](#telemetry-and-monitoring)
10. [Advanced Usage](#advanced-usage)

## 1. Installation

To install ESIHub, use pip:

```bash
pip install esihub-client
```

## 2. Client Initialization

You can initialize the ESIHubClient with or without SSO capabilities:

```python
from esihub import ESIHubClient

# Without SSO
client = ESIHubClient()

# With SSO
client_with_sso = ESIHubClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    redirect_uri="your_redirect_uri"
)
```

## 3. Making Requests

To make a request to the ESI API:

```python
async with ESIHubClient() as client:
    response = await client.request("GET", "/universe/systems/", token="your_access_token")
    print(response)
```

## 4. Pagination

For endpoints that support pagination:

```python
async with ESIHubClient() as client:
    async for page in client.paginate("GET", "/characters/12345/assets/", token="your_access_token"):
        print(page)
```

## 5. SSO (Single Sign-On)

If you've initialized the client with SSO capabilities:

```python
async with ESIHubClient(client_id="id", client_secret="secret", redirect_uri="uri") as client:
    # Get authorization URL
    auth_url = await client.get_authorization_url()
    print(f"Please visit: {auth_url}")

    # After user authorizes, they'll be redirected with a code
    code = input("Enter the code from the redirect URL: ")
    token = await client.fetch_token(code)

    # Use the token for authenticated requests
    character_info = await client.request("GET", "/characters/12345/", token=token['access_token'])
    print(character_info)

    # Refresh the token when it expires
    new_token = await client.refresh_token(token['refresh_token'])
```

## 6. Caching

ESIHub uses Redis for caching by default. Ensure you have Redis running, or configure a different caching mechanism:

```python
from esihub.core.cache import Cache

custom_cache = Cache(redis_url="redis://your-custom-redis:6379")
client = ESIHubClient(cache=custom_cache)
```

## 7. Rate Limiting

ESIHub handles rate limiting automatically. To customize:

```python
from esihub.core.rate_limiter import RateLimiter

custom_limiter = RateLimiter(rate=100, per=1.0)  # 100 requests per second
client = ESIHubClient(rate_limiter=custom_limiter)
```

## 8. Error Handling

ESIHub uses custom exceptions:

```python
from esihub.exceptions import ESIHubException, ServerError

try:
    response = await client.request("GET", "/some/endpoint/")
except ServerError as e:
    print(f"Server error: {e}")
except ESIHubException as e:
    print(f"General error: {e}")
```

## 9. Telemetry and Monitoring

### OpenTelemetry

ESIHub integrates with OpenTelemetry for distributed tracing:

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

trace.set_tracer_provider(TracerProvider())
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))
```

### Prometheus

ESIHub exposes Prometheus metrics. To use them:

```python
from prometheus_client import start_http_server

# Start Prometheus HTTP server
start_http_server(8000)

# Your ESIHub client usage here
# Metrics will be available at http://localhost:8000
```

Available metrics:
- `esihub_requests_total`: Total number of requests made
- `esihub_request_duration_seconds`: Histogram of request durations

## 10. Advanced Usage

### Custom Session Management

For more control over the aiohttp ClientSession:

```python
from esihub.core.connection_pool import ConnectionPool

custom_pool = ConnectionPool(pool_size=200)
client = ESIHubClient(connection_pool=custom_pool)
```

### Version Management

ESIHub automatically uses the latest stable version of the ESI API. To use a specific version:

```python
response = await client.request("GET", "/universe/systems/", version="v1")
```

### Performance Monitoring

Access performance metrics:

```python
from esihub.utils.performance import performance_monitor

metrics = performance_monitor.get_metrics()
print(f"Average request time: {metrics['average_request_time']} seconds")
print(f"Total requests: {metrics['total_requests']}")
```

This detailed guide covers all major features of the ESIHub client. Always refer to the [official ESI documentation](https://esi.evetech.net/) for the most up-to-date information on available endpoints and their parameters.