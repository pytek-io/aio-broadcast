import asyncio

import pytest
import random
from aio_broadcast import MultiQueue, broadcast

random.seed(0)
pytestmark = pytest.mark.asyncio

ENOUGH_TIME_TO_LAUNCH_ALL_TASKS = 0.01


async def test_lockstep():
    async def check_next_value(consumer, value):
        assert await consumer.__anext__() == value

    queue = MultiQueue()
    nb_values = 10
    nb_consumers = 10
    consumers = [queue.__aiter__() for _ in range(nb_consumers)]
    for i in range(nb_values):
        queue.put(i)
        await asyncio.gather(
            *(
                asyncio.create_task(check_next_value(consumer, i))
                for consumer in consumers
            )
        )


async def test_close():
    queue = MultiQueue()
    nb_values = 10
    nb_consumers = 1

    async def consume():
        total = 0
        async for value in queue:
            print(value)
            total += value
        return total

    tasks = [asyncio.create_task(consume()) for _ in range(nb_consumers)]
    await asyncio.sleep(ENOUGH_TIME_TO_LAUNCH_ALL_TASKS)
    for i in range(nb_values):
        queue.put(i)
    # closing the queue before any consumer has processed any value
    queue.close()
    total_sum = sum(await asyncio.gather(*tasks))
    assert total_sum == ((nb_values - 1) * nb_values / 2) * nb_consumers


async def consume_stream(stream):
    received = []
    async for i in stream:
        await asyncio.sleep(random.uniform(0, 0.01))
        received.append(i)
    return received


async def feed_stream(values):
    for value in values:
        await asyncio.sleep(random.uniform(0, 0.05))
        yield value


async def test_broadcast_async_gen():
    values = list(range(500))
    source_stream = broadcast(feed_stream(values))
    test = await asyncio.gather(
        *[consume_stream(source_stream) for _ in range(30)],
    )
    assert all(values == received for received in test)
