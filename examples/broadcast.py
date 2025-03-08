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
