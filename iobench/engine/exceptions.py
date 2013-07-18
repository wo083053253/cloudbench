#coding:utf-8

class FIOException(Exception):
    pass


class FIOCallException(FIOException):
    def __init__(self, code, stdout, stderr):
        self.code = code
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self):
        return "[{0}]:\n    {1}\n    {2}".format(self.code, self.stdout, self.stderr)


class FIOInvalidVersion(FIOException):
    pass


class FIOInvalidConfigValue(FIOException):
    pass
