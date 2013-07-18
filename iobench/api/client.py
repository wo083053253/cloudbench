#coding:utf-8
import requests

from iobench.api.factory import make_api_methods
from iobench.api.util import path_join


class Client(object):
    _api_path = "api"
    _api_version = "v1"

    def __init__(self, host, auth=None):
        self.host = host
        self._session = requests.Session()
        self._session.headers = {"Accept": "application/json"}
        self._session.auth = auth

    @property
    def base_api_path(self):
        return path_join(self._api_path, self._api_version)


    create_instance, \
    list_instances, \
    get_instance, \
    get_or_create_instance = make_api_methods("instance")

    create_measurement, \
    list_measurements, \
    get_measurement, \
    get_or_create_measurement = make_api_methods("measurement")

    create_datapoint, \
    list_datapoints, \
    get_datapoint, \
    get_or_create_datapoint = make_api_methods("datapoint")