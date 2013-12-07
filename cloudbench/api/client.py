#coding:utf-8
import logging
import time
import random
from functools import wraps

import requests

from cloudbench.api.exceptions import NoSuchObject, MultipleObjectsReturned, APIError, DuplicateObject
from cloudbench.api.factory import _get_by_url, _list_objects, _create_object, _update_object
from cloudbench.api.util import path_join, _normalize_api_path


logger = logging.getLogger(__name__)


def counter():
    i = 0
    while 1:
        yield i
        i += 1


def api_wrapper(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):

        for n_failures in counter():
            try:
                return method(self, *args, **kwargs)
            except (requests.HTTPError, requests.Timeout, requests.ConnectionError) as e:
                response = None
                logger.exception("An API call failed")
                if hasattr(e, "response"):
                    response = e.response
                    logger.error("%s %s", response.status_code, response.reason)
                    logger.error(e.response.text)

                if n_failures >= self.retry_max:
                    raise APIError(response)

                retry_in = max(0, self.retry_wait + self.retry_range * (1 - 2 * random.random()))
                logger.info("Retrying API call in %s seconds", retry_in)
                time.sleep(retry_in)

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
            try:
                return self.create(**filters)
            except DuplicateObject:
                return self.get(**filters)

    @property
    def retry_max(self):
        return self.client.retry_max

    @property
    def retry_wait(self):
        return self.client.retry_wait

    @property
    def retry_range(self):
        return self.client.retry_range


class Client(object):
    _api_path = "api"
    _api_version = "v1"

    def __init__(self, host, auth=None, retry_max=0, retry_wait=0, retry_range=0):
        self.host = host
        self.retry_max = retry_max
        self.retry_wait = retry_wait
        self.retry_range = retry_range

        self._session = requests.Session()
        self._session.headers = {"accept": "application/json"}
        self._session.auth = auth

        self.providers = ResourceHandler(self, "provider")
        self.locations = ResourceHandler(self, "location")
        self.abstract_assets = ResourceHandler(self, "abstractasset")
        self.physical_assets = ResourceHandler(self, "physicalasset")
        self.configurations = ResourceHandler(self, "configuration")
        self.measurements = ResourceHandler(self, "measurement")
        self.measurement_assets = ResourceHandler(self, "measurementasset")

    @property
    def base_api_path(self):
        return path_join(self._api_path, self._api_version)

    @api_wrapper
    def update(self, obj):
        logger.debug("UPDATE: %s", obj["resource_uri"])
        _update_object(self._session, self.host, obj)
