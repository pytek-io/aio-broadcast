import asyncio
from aio_broadcast import broadcast
import random
from typing import AsyncIterator, Iterable

random.seed(0)


async def consume_stream(stream: AsyncIterator[int], name: str):
    async for value in stream:
        await asyncio.sleep(random.uniform(0, 0.1))
        print(name, value)


async def stream(values: Iterable[int]):
    for value in values:
        await asyncio.sleep(random.uniform(0, 0.5))
        yield value


async def main():
    values = list(range(5))
    source_stream = broadcast(stream(values))
    await asyncio.gather(
        *[consume_stream(source_stream, f"consumer {i}") for i in range(3)],
    )


asyncio.run(main())
