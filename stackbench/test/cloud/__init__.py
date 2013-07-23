#coding:utf-8
import os.path


def boto_importable():
    try:
        import boto
    except ImportError:
        return False
    return True


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