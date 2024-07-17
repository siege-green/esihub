# Authentication

ESIHub uses EVE Online's Single Sign-On (SSO) system for authentication. This guide will walk you through the process of authenticating your application and managing tokens.

## Setting Up SSO

1. Register your application on the [EVE Developers site](https://developers.eveonline.com/).
2. Note your Client ID and Secret Key.
3. Set up your callback URL.

## Initializing the Client

```python
from esihub import ESIHubClient

client = ESIHubClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    callback_url="your_callback_url"
)
```

## Getting an Authorization URL

```python
auth_url = await client.get_authorize_url()
print(f"Please visit this URL to authorize: {auth_url}")
```

## Exchanging the Code for Tokens

After the user authorizes your application, they will be redirected to your callback URL with a code parameter. Use this code to get access and refresh tokens:

```python
code = "code_from_callback_url"
tokens = await client.get_access_token(code)
```

## Using Tokens for Requests

```python
character_id = 12345
character_info = await client.get_characters_character_id(character_id=character_id, token=tokens['access_token'])
```

## Refreshing Tokens

ESIHub automatically handles token refreshing. If a token is about to expire, it will be refreshed before making the request.

## Token Storage

ESIHub doesn't handle long-term token storage. You should implement secure storage for tokens in your application, such as an encrypted database.

Remember to always keep your Client Secret and user tokens secure!