import threading
import queue
from concurrent.futures import ThreadPoolExecutor


_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="luaroad")


def run_in_thread(fn, *args, **kwargs):
    return _executor.submit(fn, *args, **kwargs)


class AsyncTask:
    def __init__(self, target, callback=None):
        self._target = target
        self._callback = callback
        self._result = None
        self._error = None
        self._done = False

    def run(self):
        try:
            self._result = self._target()
        except Exception as e:
            self._error = e
        finally:
            self._done = True
            if self._callback:
                self._callback(self._result, self._error)
