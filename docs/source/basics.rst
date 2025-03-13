MultiQueue
==========

This container can be iterated through asynchronously using async for syntax. Unlike other implementations it does not rely on subscription mechanism.

..  code-block:: python

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

broadcast
=========

This method wraps an aync generator into an object that can be iterated through simultanously.

..  code-block:: python

    import asyncio
    from aio_broadcast import broadcast
    import random

    random.seed(0)


    async def consume_stream(stream, name):
        async for value in stream:
            await asyncio.sleep(random.uniform(0, 0.1))
            print(name, value)


    async def stream(values):
        for value in values:
            await asyncio.sleep(random.uniform(0, 0.5))
            yield value


    async def main():
        values = list(range(5))
        source_stream = broadcast(stream(values))
        await asyncio.gather(
            *[consume_stream(source_stream) for _ in range(3)],
        )


    asyncio.run(main())
