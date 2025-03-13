import asyncio
from aio_broadcast import MultiQueue


async def print_stream(stream, name, delay):
    async for i in stream:
        await asyncio.sleep(delay)
        print(name, i)


async def main():
    stream = MultiQueue()
    consumers = [asyncio.create_task(print_stream(stream, f"consumer {i}", 1 / (i + 1))) for i in range(5)]
    for i in range(5):
        await asyncio.sleep(0.2)
        stream.put(i)
    stream.close()
    await asyncio.gather(*consumers)


asyncio.run(main())
