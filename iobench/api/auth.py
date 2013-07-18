#coding:utf-8
from requests.auth import AuthBase


class APIKeyAuth(AuthBase):
    """Attaches API Key Authentication to the given Request or Session object."""
    def __init__(self, username, api_key):
        self.username = username
        self.api_key = api_key

    def __call__(self, r):
        r.headers['Authorization'] = "ApiKey {0}:{1}".format(self.username, self.api_key)
        return r