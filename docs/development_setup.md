# Development Setup

This guide will help you set up your development environment for contributing to ESIHub.

## Prerequisites

- Python 3.11 or higher
- poetry (Python package manager)
- Git

## Setting Up Your Development Environment

1. Fork the ESIHub repository on GitHub.

2. Clone your fork locally:
   ```
   git clone https://github.com/siege-green/esihub.git
   cd esihub
   ```

3. Create a virtual environment:
   ```
   python -m venv venv
   ```

4. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```

5. Install the development dependencies:
   ```
   poetry install
   ```


## Running Tests

To run the test suite:

```
pytest
```

## Code Style

We use [Black](https://github.com/psf/black) for code formatting and [isort](https://pycqa.github.io/isort/) for import sorting. You can format your code by running:

```
black .
isort .
```

## Building Documentation

To build the documentation locally:

```
cd docs
make html
```

The built documentation will be in the `docs/_build/html` directory.

## Setting Up ESI API Credentials

To run integration tests or use ESIHub for development, you'll need to set up ESI API credentials:

1. Go to the [EVE Developers Portal](https://developers.eveonline.com/).
2. Create a new application or use an existing one.
3. Set the following environment variables with your credentials:
   ```
   export ESI_CLIENT_ID=your_client_id
   export ESI_CLIENT_SECRET=your_client_secret
   export ESI_CALLBACK_URL=your_callback_url
   ```

Now you're all set to start developing with ESIHub!