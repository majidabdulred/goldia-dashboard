# async_runner.py (or put near top of your main module)
import asyncio
from threading import Thread
from concurrent.futures import wait

class AsyncLoopThread:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self._thread = Thread(target=self._start_loop, daemon=True, name="async-loop-thread")
        self._thread.start()

    def _start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def submit(self, coro):
        """Return concurrent.futures.Future from run_coroutine_threadsafe"""
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

# create a single global runner used by all calls
async_runner = AsyncLoopThread()