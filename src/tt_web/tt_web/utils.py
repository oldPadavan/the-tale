
import json
import asyncio

from . import exceptions


class Lock:
    __slots__ = ('_point', 'key', '_lock', 'loop', 'timeout')

    def __init__(self, point, key, lock, loop=None, timeout=None):
        self._point = point
        self._lock = lock

        self.key = key
        self.loop = loop
        self.timeout = timeout

    async def acquire(self):
        try:
            await asyncio.wait_for(self._lock.acquire(), timeout=self.timeout, loop=self.loop)
        except asyncio.TimeoutError:
            raise exceptions.SyncPointTimeoutError(key=self.key, timeout=self.timeout)

    def release(self):
        if not self._lock._waiters:
            del self._point._locks[self.key]

        self._lock.release()

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.release()


class SyncPoint:
    __slots__ = ('_locks',)

    def __init__(self):
        self._locks = {}

    def lock(self, key, loop=None, timeout=None):
        if key not in self._locks:
            self._locks[key] = asyncio.Lock(loop=loop)

        return Lock(point=self, key=key, lock=self._locks[key], loop=loop, timeout=timeout)


def load_config(path):
    with open(path) as f:
        return json.load(f)
