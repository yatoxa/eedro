import asyncio
import collections
import logging
from typing import Optional


class LimitExceeded(Exception):
    pass


class RateLimiter:
    def __init__(
        self,
        limit: int,
        *,
        period: int = 1,
        label: Optional[str] = None,
    ) -> None:
        self._period = period
        self._limit = limit
        self._label = label
        self._counter = None
        self._tasks = []
        self._stop = False
        self._by_key_limiters = {}
        self._waiters = collections.deque()
        self._loop = asyncio.get_running_loop()

    def _release_waiters(self, every=False) -> None:
        waiters_count = len(self._waiters)
        limit = waiters_count if every else min(waiters_count, self._limit)

        for _ in range(limit):
            waiter = self._waiters.popleft()

            if not waiter.done():
                waiter.set_result(None)

    async def _limit_controller(self) -> None:
        while not self._stop:
            self._counter = 0
            self._release_waiters()
            await asyncio.sleep(self._period)

            if self._label is not None:
                logging.debug(
                    "%s has %d RPS and waiters queue size: %d",
                    self._label,
                    self._counter,
                    len(self._waiters),
                )

    async def run(self) -> None:
        self._tasks.append(asyncio.create_task(self._limit_controller()))
        await asyncio.sleep(0)

    async def __aenter__(self) -> "RateLimiter":
        await self.run()
        return self

    async def stop(self) -> None:
        await asyncio.gather(bkl.stop() for bkl in self._by_key_limiters.values())
        self._stop = True

        for task in self._tasks:
            task.cancel()

        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._release_waiters(every=True)

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.stop()

    async def _wait(self) -> None:
        waiter = self._loop.create_future()
        self._waiters.append(waiter)
        await waiter

    async def acquire_limit(self, *, no_wait: bool = False) -> int:
        if self._limit == 0:
            return 0

        if self._counter is None:
            await self.run()

        while self._counter >= self._limit:
            if no_wait:
                raise LimitExceeded

            await self._wait()

        self._counter += 1
        return self._counter

    async def acquire_limit_by_key(self, key: str, *, no_wait: bool = False) -> int:
        try:
            limiter = self._by_key_limiters[key]
        except KeyError:
            limiter = self._by_key_limiters[key] = self.__class__(
                self._limit,
                period=self._period,
                label=self._label,
            )

        return await limiter.acquire_limit(no_wait=no_wait)
