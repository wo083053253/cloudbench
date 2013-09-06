#coding:utf-8
import logging
from functools import wraps

import requests
from requests.exceptions import HTTPError

from cloudbench.api.exceptions import NoSuchObject, MultipleObjectsReturned, APIError
from cloudbench.api.factory import _get_by_url, _list_objects, _create_object
from cloudbench.api.util import path_join, _normalize_api_path


logger = logging.getLogger(__name__)


def api_wrapper(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except HTTPError as e:
            response = None
            if hasattr(e, "response"):
                response = e.response
                logging.error("An API call failed")
                logging.error("%s %s", response.status_code, response.reason)
                logging.error(e.response.text)
            raise APIError(response)
    return wrapper


class ResourceHandler(object):
    def __init__(self, client, resource):
        self.client = client
        self.resource =   _normalize_api_path(resource)

    @api_wrapper
    def create(self, **kwargs):
        logger.debug("CREATE: %s", self.resource)
        location = _create_object(self.client._session, self.client.host,
                                  path_join(self.client.base_api_path, self.resource), kwargs)
        return _get_by_url(self.client._session, location)

    @api_wrapper
    def list(self, **filters):
        logger.debug("LIST: %s", self.resource)
        return _list_objects(self.client._session, self.client.host,
                             path_join(self.client.base_api_path, self.resource), filters)

    @api_wrapper
    def get(self, **filters):
        matches = self.list(**filters)
        if not matches:
            raise NoSuchObject()
        if len(matches) > 1:
            raise MultipleObjectsReturned()
        # The API might return different results for a get and a list - we'll be safe and waste an API call here
        logger.debug("GET: %s", self.resource)
        return _get_by_url(self.client._session, path_join(self.client.host, matches.pop()["resource_uri"]))

    @api_wrapper
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
        self._session.headers = {"accept": "application/json"}
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

