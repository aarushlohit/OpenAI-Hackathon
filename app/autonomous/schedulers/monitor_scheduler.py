import asyncio
from collections.abc import Awaitable, Callable


class MonitorScheduler:
    async def run_once(self, task: Callable[[], Awaitable[None]]) -> None:
        await task()

    async def run_periodic(self, task: Callable[[], Awaitable[None]], interval_seconds: float) -> None:
        while True:
            await task()
            await asyncio.sleep(interval_seconds)

