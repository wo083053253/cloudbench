#coding:utf-8
import subprocess


try:
    __import__("boto")
except ImportError:
    boto_importable = False
else:
    boto_importable = True


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

