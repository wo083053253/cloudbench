#coding:utf-8

class APIError(Exception):
    pass

class NoSuchObject(APIError):
    pass

class MultipleObjectsReturned(APIError):
    pass
