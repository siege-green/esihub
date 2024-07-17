# ESIHub

[![PyPI version](https://badge.fury.io/py/esihub.svg)](https://badge.fury.io/py/esihub)
[![Python Versions](https://img.shields.io/pypi/pyversions/esihub.svg)](https://pypi.org/project/esihub/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/meloncafe/esihub/graph/badge.svg?token=Q5Un3rLAsw)](https://codecov.io/gh/meloncafe/esihub)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A high-performance, feature-rich Python client for the EVE Online ESI API

[Installation](#installation) •
[Quick Start](#quick-start) •
[Features](#features) •
[Documentation](#documentation) •
[Contributing](#contributing) •
[License](#license)

## Installation

ESIHub requires Python 3.11 or later. Install it with pip:

```bash
pip install esihub
```

## Quick Start

Here's a simple example to get you started:

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

## Features

- ⚡ **Asynchronous Operations**: Built on `aiohttp` for high performance
- 🔄 **Automatic Rate Limiting**: Stay within EVE Online's API guidelines
- 💾 **Efficient Caching**: Reduce unnecessary API calls with Redis integration
- 🔑 **Token Management**: Automatic token refresh and secure storage
- 🛡️ **Robust Error Handling**: Custom exceptions for different error scenarios
- 📝 **Comprehensive Logging**: Detailed logs for easy debugging
- 🎣 **Event Hooks**: Lifecycle events for request customization
- 📦 **Batch Processing**: Make multiple requests concurrently
- ⚙️ **Easy Configuration**: Simple setup with environment variables

## Advanced Usage

### Batch Requests

Make multiple requests concurrently:

```python
results = await client.batch_request([
    {"method": "GET", "path": "/characters/123/"},
    {"method": "GET", "path": "/characters/456/"}
])
```

### Event Hooks

Register event hooks for request lifecycle events:

```python
@client.event_system.on('before_request')
def on_before_request(**kwargs):
    print(f"About to make a request: {kwargs['method']} {kwargs['path']}")

@client.event_system.on('after_request')
def on_after_request(**kwargs):
    print(f"Request completed: {kwargs['method']} {kwargs['path']}")
```

### Configuration

Set configuration options using environment variables:

```bash
export ESI_CLIENT_ID=your_client_id
export ESI_CLIENT_SECRET=your_client_secret
export ESI_CALLBACK_URL=your_callback_url
export ESI_REDIS_URL=redis://localhost
export ESI_LOG_LEVEL=INFO
```

## Documentation

For full documentation, please visit our [GitHub Pages](https://esihub.siege-green.com).

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for more details.

## License

ESIHub is released under the MIT License. See the [LICENSE](LICENSE) file for more details.
