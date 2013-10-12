#coding:utf-8

class APIError(Exception):
    def __init__(self, response=None):
        self.response = response

    def __repr__(self):
        if self.response is not None:
            return self.response.text

    def __str__(self):
        return repr(self)

class NoSuchObject(APIError):
    pass

class MultipleObjectsReturned(APIError):
    pass

class DuplicateObject(APIError):
    pass