# Examples

This document provides practical examples of using ESIHub in various scenarios.

## Basic Character Information

```python
import asyncio
from esihub import ESIHubClient

async def get_character_info(character_id: int):
    async with ESIHubClient(...) as client:
        info = await client.get_characters_character_id(character_id=character_id)
        print(f"Character Name: {info['name']}")
        print(f"Corporation ID: {info['corporation_id']}")

asyncio.run(get_character_info(12345))
```

## Corporation Assets

```python
import asyncio
from esihub import ESIHubClient

async def get_corporation_assets(corporation_id: int, token: str):
    async with ESIHubClient(...) as client:
        assets = []
        async for page in client.get_corporations_corporation_id_assets(corporation_id=corporation_id, token=token):
            assets.extend(page)
        print(f"Total assets: {len(assets)}")

asyncio.run(get_corporation_assets(67890, "access_token_here"))
```

## Market Orders

```python
import asyncio
from esihub import ESIHubClient

async def get_market_orders(region_id: int, type_id: int):
    async with ESIHubClient(...) as client:
        orders = await client.get_markets_region_id_orders(
            region_id=region_id,
            type_id=type_id,
            order_type='all'
        )
        print(f"Total orders: {len(orders)}")
        print(f"Lowest sell price: {min(order['price'] for order in orders if order['is_buy_order'] == False)}")
        print(f"Highest buy price: {max(order['price'] for order in orders if order['is_buy_order'] == True)}")

asyncio.run(get_market_orders(10000002, 34))  # Tritanium in The Forge
```

## Batch Requests

```python
import asyncio
from esihub import ESIHubClient

async def get_multiple_characters(character_ids: list):
    async with ESIHubClient(...) as client:
        requests = [
            {"method": "GET", "path": f"/characters/{char_id}/", "character_id": char_id}
            for char_id in character_ids
        ]
        results = await client.batch_request(requests)
        for result in results:
            print(f"Character Name: {result['name']}")

asyncio.run(get_multiple_characters([12345, 67890, 13579]))
```

These examples demonstrate some common use cases for ESIHub. Remember to replace the placeholder values (client initialization parameters, character IDs, access tokens) with your actual data when using these examples.