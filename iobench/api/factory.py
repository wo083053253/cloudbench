#coding:utf-8
import json
from iobench.api.exceptions import NoSuchObject, MultipleObjectsReturned

from iobench.api.util import _normalize_api_path, path_join

API_ONLY_KW = ["limit", "offset"]


def _get_by_url(session, url):
    res = session.get(url)
    res.raise_for_status()
    return res.json()


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

    res = session.get(path_join(api_host, api_path), params=filters)
    res.raise_for_status()
    content = res.json()
    _extend_list.extend(content["objects"])

    return _list_objects(session, api_host, content["meta"]["next"], filters, _extend_list)


def make_api_methods(resource):
    normalized_resource_name = _normalize_api_path(resource)

    def create_method(self, **kwargs):
        headers = {"Content-Type": "application/json"}
        res = self._session.post(path_join(self.host, self.base_api_path, normalized_resource_name),
                                 headers=headers, data=json.dumps(kwargs))
        res.raise_for_status()
        return _get_by_url(self._session, res.headers["location"])

    def list_method(self, **filters):
        return _list_objects(self._session, self.host, path_join(self.base_api_path, normalized_resource_name), filters)

    def get_method(self, **filters):
        matches = list_method(self, **filters)
        if not matches:
            raise NoSuchObject()
        if len(matches) > 1:
            raise MultipleObjectsReturned()
        return matches[0]

    def get_or_create_method(self, **filters):
        try:
            return get_method(self, **filters)
        except NoSuchObject:
            return create_method(self, **filters)

    return create_method, list_method, get_method, get_or_create_method
