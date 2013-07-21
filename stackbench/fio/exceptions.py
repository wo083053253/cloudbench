#coding:utf-8

class FIOError(Exception):
    pass


class FIOCallError(FIOError):
    def __init__(self, code, stdout, stderr):
        self.code = code
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self):
        return "[{0}]:\n    {1}\n    {2}".format(self.code, self.stdout, self.stderr)


class FIOInvalidVersion(FIOError):
    pass


class FIOInvalidJob(FIOError):
    pass
