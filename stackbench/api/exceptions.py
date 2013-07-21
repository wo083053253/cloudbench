#coding:utf-8

class APIError(Exception):
    def __init__(self, response=None):
        self.response = response

class NoSuchObject(APIError):
    pass

class MultipleObjectsReturned(APIError):
    pass
