# Usage Guide

## Dynamic Endpoint Methods

ESIHub uses the EVE Swagger Interface (ESI) specification to dynamically generate methods for all available API endpoints. This feature provides several benefits:

1. Intuitive method names based on API paths
2. Automatic parameter validation
3. Better IDE autocomplete support
4. Up-to-date with the latest ESI changes

### How it works

When you initialize an `ESIHubClient`, it reads the Swagger specification and generates methods for each endpoint. The method names are created by converting the URL path to a Python-friendly format.

For example:
- `/characters/{character_id}/` becomes `get_characters_character_id()`
- `/corporations/{corporation_id}/assets/` becomes `get_corporations_corporation_id_assets()`

### Using dynamic endpoint methods

Instead of using the generic `request()` method, you can use these dynamically generated methods directly:

```python
async with ESIHubClient() as client:
    # Get character information
    character_info = await client.get_characters_character_id(character_id=12345)
    
    # Get corporation assets
    corp_assets = await client.get_corporations_corporation_id_assets(corporation_id=67890)
    
    # Post a fleet invitation
    invitation_result = await client.post_fleets_fleet_id_members(
        fleet_id=123456,
        invitation={'character_id': 78901, 'role': 'squad_member'}
    )
```

### Benefits of using dynamic endpoint methods

1. **Type hinting**: The methods provide proper type hints for parameters and return values.
2. **Documentation**: Each method includes docstrings from the Swagger spec, viewable in your IDE.
3. **Validation**: Parameters are validated before making the request, catching errors early.
4. **Discoverability**: You can easily explore available methods using your IDE's autocomplete feature.

### Handling path parameters

For endpoints with path parameters (like `{character_id}`), provide these as keyword arguments:

```python
character_info = await client.get_characters_character_id(character_id=12345)
```

### Handling query parameters

For endpoints with query parameters, provide these as keyword arguments as well:

```python
search_results = await client.get_search(
    categories=['character', 'corporation'],
    search='Test'
)
```

### Handling request bodies

For POST, PUT, and PATCH methods that require a request body, provide the data as a dictionary:

```python
new_fleet = await client.post_fleets(
    create_fleet_request={
        'motd': 'Welcome to the fleet!',
        'is_free_move': True
    }
)
```

By using these dynamically generated methods, you can interact with the ESI API in a more natural and pythonic way, while benefiting from improved code completion and inline documentation in your IDE.