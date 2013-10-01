#coding:utf-8
import time

class MockTimeSleep(object):
    def __init__(self):
        self._sleep = None
        self.calls = []

    def __enter__(self):
        self._sleep = time.sleep
        time.sleep = self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        # Accept the exception params, but don't do anything about them
        if self._sleep is not None:
            time.sleep = self._sleep
        self._sleep = None

    def __call__(self, seconds):
        self.calls.append(seconds)
        return

