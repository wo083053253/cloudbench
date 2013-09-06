#coding:utf-8
class CloudError(Exception):
    """
    Base class for Cloud introspection errors
    """

class VolumeNotFoundError(CloudError):
    """
    Raised when we were unable to find a volume on the system.
    """
    def __init__(self, path):
        self.path = path

class CloudUnavailableError(CloudError):
    """
    Raised when Cloud introspection failed
    """
    def __init__(self, reason):
        self.reason = reason

class CloudAPIError(CloudError):
    """
    Raised when a Cloud API returned an error
    """
    def __init__(self, response):
        self.response = response
