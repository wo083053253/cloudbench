#coding:utf-8
import json

from fio.api.exception import InvalidDataError, APIError
from fio.api.util import _normalize_api_path, path_join

API_ONLY_KW = ["limit", "offset"]


def _get_by_url(session, url):
    res = session.get(url)
    return json.loads(res.text)


def _list_objects(session, api_host, api_path, filters, _extend_list=None):
    """
    :param session: A session object to use to make the request
    :param api_host: The host where the API is located
    :param api_path: The path where the objects are listed
    :param filters: Filters to apply to the request
    :return: The list of objects that are retrieved at  this endpoint
    :rtype: list
    """
    _extend_list = _extend_list if _extend_list is not None else []

    if api_path is None:
        return _extend_list

    for kw in API_ONLY_KW:
        assert kw not in filters, "You can't use the {0} pagination keyword".format(kw) #TODO: Accept on the first hit

    r = session.get(path_join(api_host, api_path), params=filters)
    response = json.loads(r.text)
    _extend_list.extend(response["objects"])

    return _list_objects(session, api_host, response["meta"]["next"], filters, _extend_list)


def make_create_method(path):
    def api_method(self, **kwargs):
        headers = {"Content-Type": "application/json"}
        r = self._session.post(path_join(self.host, self.base_api_path, _normalize_api_path(path)),
                               headers=headers, data=json.dumps(kwargs))

        if r.status_code == 201:
            return _get_by_url(self._session, r.headers["location"])

        ExcClass = APIError
        if r.status_code == 400:
            ExcClass = InvalidDataError
        raise ExcClass(r)

    return api_method


def make_list_method(path):
    def api_method(self, **filters):
        return _list_objects(self._session, self.host, path_join(self.base_api_path, _normalize_api_path(path)), filters)
    return api_method

