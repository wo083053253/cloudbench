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


    create_asset, \
    list_assets, \
    get_asset, \
    get_or_create_asset = make_api_methods("asset")

    create_configuration, \
    list_configurations, \
    get_configuration, \
    get_or_create_configuration = make_api_methods("configuration")

    create_measurement, \
    list_measurements, \
    get_measurement, \
    get_or_create_measurement = make_api_methods("measurement")
