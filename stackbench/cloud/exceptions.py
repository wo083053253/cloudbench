#coding:utf-8
class CloudError(Exception):
    """
    Base class for Cloud introspection errors
    """

class VolumeUnavailableError(CloudError):
    """
    Raised when a volume is unavailable (not mounted yet)
    """
    def __init__(self, volume):
        self.volume = volume

class VolumeNotFoundError(VolumeUnavailableError):
    """
    Raised when we were unable to find a volume on the system.
    """

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
