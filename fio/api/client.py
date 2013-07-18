#coding:utf-8
import requests

from fio.api.factory import make_list_method, make_create_method
from fio.api.util import path_join


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

    list_instances = make_list_method("instance")

    list_measurements = make_list_method("measurement")
    create_measurement = make_create_method("measurement")

    list_datapoints = make_list_method("datapoint")
    create_datapoint = make_create_method("datapoint")
