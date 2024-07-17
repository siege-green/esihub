# Welcome to ESIHub

ESIHub is a powerful, asynchronous Python client for interacting with the EVE Online ESI (EVE Swagger Interface) API. It provides developers with a robust, efficient, and easy-to-use interface for building EVE Online applications.

## Navigation

- [Authentication](authentication.md)
- [API Reference](api_reference.md)
- [Advanced Usage](advanced_usage.md)
- [Configuration](configuration.md)
- [Error Handling](error_handling.md)
- [Examples](examples.md)
- [Development Setup](development_setup.md)
- [Contributing](../CONTRIBUTING.md)

## Key Features

- **Asynchronous Operations**: Built on `aiohttp` for high-performance API interactions
- **Automatic Rate Limiting**: Stay within EVE Online's API usage guidelines effortlessly
- **Efficient Caching**: Reduce unnecessary API calls with Redis integration
- **Token Management**: Automatic token refresh and secure storage
- **Robust Error Handling**: Custom exceptions for different error scenarios
- **Comprehensive Logging**: Detailed logs for easy debugging and monitoring
- **Event System**: Customizable hooks for request lifecycle events
- **Batch Request Processing**: Make multiple requests concurrently for improved performance
- **Easy Configuration**: Simple setup with environment variables
- **Extensive Test Coverage**: Ensure reliability with our comprehensive test suite
- **Python 3.11+ Support**: Leverage the latest Python features for improved performance and type hinting

## Quick Start

Here's a simple example to get you started with ESIHub:

```python
import asyncio
from esihub import ESIHubClient

async def main():
    client = ESIHubClient(
        client_id="your_client_id",
        client_secret="your_client_secret",
        callback_url="your_callback_url"
    )

    async with client:
        # Get character information
        character_id = 12345
        character_info = await client.get_characters_character_id(character_id=character_id)
        print(f"Character Info: {character_info}")

asyncio.run(main())
```

## Installation

You can install ESIHub using pip:

```bash
pip install esihub
```

## Documentation

- [Authentication](authentication.md): Learn how to authenticate with the EVE Online SSO
- [API Reference](api_reference.md): Detailed documentation of all available methods
- [Advanced Usage](advanced_usage.md): Explore advanced features like caching, rate limiting, and event hooks
- [Configuration](configuration.md): Learn how to configure ESIHub for your needs
- [Error Handling](error_handling.md): Understand how to handle different types of errors
- [Examples](examples.md): See ESIHub in action with real-world examples

## Contributing

We welcome contributions to ESIHub! If you'd like to contribute, please check out our [Contributing Guide](../CONTRIBUTING.md).

## Support

If you encounter any issues or have questions, please file an issue on our [GitHub repository](https://github.com/yourusername/esihub/issues).

Happy coding with ESIHub!