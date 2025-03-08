from __future__ import annotations
import asyncio
from typing import AsyncIterator, Generic, Optional, TypeVar, cast, Union

T = TypeVar("T")


class Sentinel:
    pass


queue_closed = Sentinel()


class Link(Generic[T]):
    def __init__(self, item: Optional[T] = None) -> None:
        self.item = item
        self.next: Union[Link[T], None, Sentinel] = None


class Broadcast(Generic[T]):
    def __init__(self):
        self.current_link = Link()
        self.updated = asyncio.Event()

    def __aiter__(self) -> AsyncIterator[T]:
        return Iterator(self)

    def put(self, item: T):
        self.current_link.item = item
        self.current_link.next = Link()
        self.current_link = self.current_link.next
        self.updated.set()
        self.updated = asyncio.Event()

    def close(self):
        self.current_link.next = queue_closed
        self.updated.set()


class Iterator(AsyncIterator[T]):
    def __init__(self, queue: Broadcast[T]):
        self.queue: Broadcast[T] = queue
        self.current_link: Link[T] = queue.current_link

    async def __anext__(self) -> T:
        if self.current_link.next is None:
            await self.queue.updated.wait()
        if self.current_link.next is queue_closed:
            raise StopAsyncIteration
        item = self.current_link.item
        # next will be a Link once updated is set
        self.current_link = cast(Link, self.current_link.next)
        return cast(T, item)
