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
