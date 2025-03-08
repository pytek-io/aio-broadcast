[![Coverage](https://codecov.io/gh/pytek-io/aio-broadcast/branch/main/graph/badge.svg)](https://codecov.io/gh/pytek-io/aio-broadcast)

This library provides ways to iterate through an async generator multiple times at once, as demonstrated below.

``` python
import asyncio
from aio_broadcast import broadcast
import random

random.seed(0)


async def consume_stream(stream):
    received = []
    async for i in stream:
        await asyncio.sleep(random.uniform(0, .1))
        received.append(i)
    return received


async def feed_stream(values):
    for value in values:
        await asyncio.sleep(random.uniform(0, 0.5))
        yield value


async def main():
    values = list(range(5))
    source_stream = broadcast(feed_stream(values))
    results = await asyncio.gather(
        *[consume_stream(source_stream) for _ in range(3)],
    )
    assert all(values == received for received in results)


asyncio.run(main())
```

It also provides a queue that can be iterated through multiple times at once, as demonstrated below.

``` python
import asyncio
from aio_broadcast import Broadcast


async def print_stream(stream, name, delay):
    async for i in stream:
        await asyncio.sleep(delay)
        print(name, i)


async def feed_stream(nb_values, live_stream: Broadcast[int]):
    for i in range(nb_values):
        await asyncio.sleep(0.2)
        live_stream.put(i)
    live_stream.close()


async def main():
    source_stream = Broadcast()
    await asyncio.gather(
        feed_stream(5, source_stream),
        print_stream(source_stream, "fast", 0.5),
        print_stream(source_stream, "slow", 1),
    )

asyncio.run(main())
```


```
fast 0
slow 0
fast 1
slow 1
fast 2
fast 3
slow 2
fast 4
slow 3
slow 4
```