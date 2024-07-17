# Python 3.11 Features in ESIHub

ESIHub leverages several new features introduced in Python 3.11 to improve performance, code quality, and developer experience. This document outlines these features and how they are used in ESIHub.

## 1. Improved Error Messages

Python 3.11 provides more precise error locations and better error messages. This helps in debugging ESIHub code and identifying issues more quickly. For example:

```python
try:
    # Some ESIHub operation
except ESIHubException as e:
    print(f"An error occurred: {e}")
    # The error message will now include more context and precise location
```

## 2. Faster CPython

Python 3.11 includes significant performance improvements in the CPython interpreter. ESIHub benefits from these improvements, resulting in faster execution times for your EVE Online API interactions.

## 3. Enhanced Type Hinting

ESIHub uses the new type hinting features in Python 3.11, including:

- The ability to use `Self` type for more accurate method return annotations.
- Improved support for `TypedDict`, which is used in ESIHub for better type hinting of dictionary responses from the ESI API.

Example:

```python
from typing import TypedDict, Self

class Character(TypedDict):
    id: int
    name: str

class ESIHubClient:
    def get_character(self, character_id: int) -> Character:
        # ...

    def with_base_url(self, base_url: str) -> Self:
        self.base_url = base_url
        return self
```

## 4. Exception Groups

ESIHub uses exception groups to handle multiple exceptions that may occur during batch operations:

```python
try:
    results = await client.batch_request([...])
except* ESIHubException as eg:
    for exc in eg.exceptions:
        print(f"Operation failed: {exc}")
```

## 5. Improved Asyncio Support

ESIHub leverages the improved asyncio support in Python 3.11, including:

- The new `asyncio.TaskGroup` for managing groups of related tasks.
- Improved task cancellation and error handling in asyncio.

Example:

```python
async with asyncio.TaskGroup() as tg:
    character_task = tg.create_task(client.get_characters_character_id(character_id=123))
    corporation_task = tg.create_task(client.get_corporations_corporation_id(corporation_id=456))

character_info = character_task.result()
corporation_info = corporation_task.result()
```

## 6. Performance Monitoring

ESIHub uses Python 3.11's improved performance monitoring tools to help identify bottlenecks and optimize code:

```python
import tracemalloc

tracemalloc.start()

# Perform some ESIHub operations

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

print("[ Top 10 ]")
for stat in top_stats[:10]:
    print(stat)
```

By utilizing these Python 3.11 features, ESIHub provides a more efficient, type-safe, and developer-friendly experience for interacting with the EVE Online ESI API.