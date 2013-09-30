#coding:utf-8
import os.path
import subprocess


try:
    __import__("boto")
except ImportError:
    boto_importable = False
else:
    boto_importable = True


class MockPathExists(object):
    def __init__(self, existing_paths):
        self.existing_paths = existing_paths
        self._exists = None

    def __call__(self, path):
        return path in self.existing_paths

    def __enter__(self):
        self._exists = os.path.exists
        os.path.exists = self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        # Accept the exception params, but don't do anything about them
        if self._exists is not None:
            os.path.exists = self._exists
        self._exists = None


class MockSubprocessCall(object):
    def __init__(self, ret_code, output):
        self.ret_code = ret_code
        self.output = output
        self._popen = None

    def __call__(self, *args, **kwargs):
        return self

    def wait(self):
        return self.ret_code

    def communicate(self):
        return self.output, ""

    def __enter__(self):
        self._popen = subprocess.Popen
        subprocess.Popen = self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._popen is not None:
            subprocess.Popen = self._popen
        self._popen = None

