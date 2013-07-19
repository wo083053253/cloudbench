#coding:utf-8
import json
import requests
from iobench.api.exceptions import NoSuchObject, MultipleObjectsReturned

from iobench.api.factory import _get_by_url, _list_objects
from iobench.api.util import path_join, _normalize_api_path


#TODO Decorate errors as APIErrors
class ResourceHandler(object):
    def __init__(self, client, resource):
        self.client = client
        self.resource =   _normalize_api_path(resource)

    def create(self, **kwargs):
        headers = {"Content-Type": "application/json"}
        res = self.client._session.post(path_join(self.client.host, self.client.base_api_path, self.resource),
                                 headers=headers, data=json.dumps(kwargs))
        res.raise_for_status()
        return _get_by_url(self.client._session, res.headers["location"])

    def list(self, **filters):
        return _list_objects(self.client._session, self.client.host, path_join(self.client.base_api_path, self.resource), filters)

    def get(self, **filters):
        matches = self.list(**filters)
        if not matches:
            raise NoSuchObject()
        if len(matches) > 1:
            raise MultipleObjectsReturned()
        # The API might return different results for a get and a list - we'll be safe and waste an API call here
        return _get_by_url(self.client._session, path_join(self.client.host, matches.pop()["resource_uri"]))

    def get_or_create(self, **filters):
        try:
            return self.get(**filters)
        except NoSuchObject:
            return self.create(**filters)


class Client(object):
    _api_path = "api"
    _api_version = "v1"

    def __init__(self, host, auth=None):
        self.host = host
        self._session = requests.Session()
        self._session.headers = {"Accept": "application/json"}
        self._session.auth = auth

        self.providers = ResourceHandler(self, "provider")
        self.locations = ResourceHandler(self, "location")
        self.abstract_assets = ResourceHandler(self, "abstractasset")
        self.physical_assets = ResourceHandler(self, "physicalasset")
        self.configurations = ResourceHandler(self, "configuration")
        self.measurements = ResourceHandler(self, "measurement")

    @property
    def base_api_path(self):
        return path_join(self._api_path, self._api_version)

