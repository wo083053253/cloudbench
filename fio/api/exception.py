#coding:utf-8

class APIError(Exception):
    """
    Base class for reporting API errors
    """
    def __init__(self, response):
        self.response = response

    def __str__(self):
        return "{0} {1}".format(self.response.status, self.response.reason)


class InvalidDataError(APIError):
    """
    Raised when you submitted invalid data
    """
    def __str__(self):
        return "{0} {1}: {2}".format(self.response.status_code, self.response.reason, self.response.text)