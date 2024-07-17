# API Reference

This document provides a detailed description of the ESIHub API.

## ESIHubClient

The main class for interacting with the EVE Online ESI API.

### Constructor

```python
ESIHubClient(client_id: str, client_secret: str, callback_url: str, base_url: str = "https://esi.evetech.net")
```

- `client_id`: Your EVE Online application's client ID.
- `client_secret`: Your EVE Online application's client secret.
- `callback_url`: The callback URL for your application.
- `base_url`: The base URL for the ESI API (default: "https://esi.evetech.net").

### Methods

#### get_authorize_url

```python
async def get_authorize_url(scopes: Optional[str] = None, state: Optional[str] = None) -> str
```

Returns the authorization URL for the EVE SSO process.

#### get_access_token

```python
async def get_access_token(code: str) -> Dict[str, Any]
```

Exchanges an authorization code for an access token.

#### refresh_token

```python
async def refresh_token(refresh_token: str) -> Dict[str, Any]
```

Refreshes an expired access token.

#### request

```python
async def request(method: str, path: str, character_id: Optional[int] = None, **kwargs) -> Dict[str, Any]
```

Makes a request to the ESI API.

#### batch_request

```python
async def batch_request(requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]
```

Makes multiple requests concurrently.

### Dynamically Generated Methods

ESIHub dynamically generates methods based on the ESI Swagger specification. These methods correspond to ESI endpoints and follow the naming convention of the `operationId` in the Swagger spec.

For example:

- `get_characters_character_id(character_id: int) -> Dict[str, Any]`
- `get_corporations_corporation_id(corporation_id: int) -> Dict[str, Any]`

Refer to the [ESI Swagger UI](https://esi.evetech.net/ui) for a complete list of available endpoints and their parameters.