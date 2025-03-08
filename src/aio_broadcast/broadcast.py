from __future__ import annotations
import asyncio
from typing import AsyncIterator, Generic, Optional, TypeVar, cast, Union

T = TypeVar("T")


class Sentinel:
    pass


queue_closed = Sentinel()


class Link(Generic[T]):
    def __init__(self, item: Optional[T] = None) -> None:
        self.value = item
        self.next: Union[Link[T], None, Sentinel] = None


class MultiQueue(Generic[T]):
    def __init__(self):
        self.current_link = Link()
        self.updated = asyncio.Event()

    def __aiter__(self) -> AsyncIterator[T]:
        return MultiQueueIterator(self)

    def put(self, item: T):
        self.current_link.value = item
        self.current_link.next = Link()
        self.current_link = self.current_link.next
        self.updated.set()
        self.updated = asyncio.Event()

    def close(self):
        self.current_link.next = queue_closed
        self.updated.set()


class MultiQueueIterator(AsyncIterator[T]):
    def __init__(self, queue: MultiQueue[T]):
        self.queue: MultiQueue[T] = queue
        self.current_link: Link[T] = queue.current_link

    async def __anext__(self) -> T:
        if self.current_link.next is None:
            await self.queue.updated.wait()
        if self.current_link.next is queue_closed:
            raise StopAsyncIteration
        item = self.current_link.value
        # next will be a Link once updated is set
        self.current_link = cast(Link, self.current_link.next)
        return cast(T, item)


class AsyncGeneratorBroadcast(Generic[T]):
    def __init__(self, source: AsyncIterator[T]):
        self.source = source
        self.current_link: Link = Link()
        self.updated: asyncio.Event = asyncio.Event()
        self.awaiting_generator = False

    def _put(self, value: T):
        self.current_link.value = value
        self.current_link.next = Link()
        self.current_link = self.current_link.next
        self.updated.set()
        self.updated = asyncio.Event()

    def __aiter__(self) -> AsyncIterator[T]:
        return AsyncGeneratorBroadcastIterator(self)

    def close(self):
        self.current_link.next = queue_closed
        self.updated.set()


class AsyncGeneratorBroadcastIterator(AsyncIterator[T]):
    def __init__(self, queue: AsyncGeneratorBroadcast[T]):
        self.queue: AsyncGeneratorBroadcast[T] = queue
        self.current_link = self.queue.current_link

    async def __anext__(self) -> T:
        if self.current_link.next is None:
            self.current_link = self.queue.current_link
            if self.queue.awaiting_generator:
                await self.queue.updated.wait()
            else:
                self.queue.awaiting_generator = True
                try:
                    self.queue._put(await self.queue.source.__anext__())
                except StopAsyncIteration:
                    self.queue.close()
                self.queue.awaiting_generator = False
        if self.current_link.next is queue_closed:
            raise StopAsyncIteration
        value = self.current_link.value
        # next will be a Link once updated is set
        self.current_link = cast(Link, self.current_link.next)
        return cast(T, value)


def broadcast(source: AsyncIterator[T]) -> AsyncGeneratorBroadcast[T]:
    return AsyncGeneratorBroadcast(source)
