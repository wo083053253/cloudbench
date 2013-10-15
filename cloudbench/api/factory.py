#coding:utf-8
import simplejson as json
from cloudbench.api.exceptions import DuplicateObject

from cloudbench.api.util import path_join

API_ONLY_KW = ["limit", "offset"]


def _get_by_url(session, url):
    res = session.get(url)
    res.raise_for_status()
    return res.json()

def _clean_related_filters(filters):
    """
    :param filters: Filters that we want to search (and fix) for related objects
    :type filters: dict
    """
    for key, value in list(filters.items()):  # I don't want a view here
        if type(value) == dict:  #TODO: Need to wrap those into API objects
            rel_id = value.get("id")
            filters[key] = rel_id
            assert rel_id is not None, "You can't filter using dicts, except for API objects."
    return filters

def _test_for_duplicate(response):
    """
    Raise an error if the response is erroring due to an attempted duplicate object
    We test this at the API level so that we bypass the retries which are on HTTP errors.
    """
    duplicate_message = "already exists"
    for elem, message in response.json().items():
        error_messages = []

        try:
            for error in message.get("__all__", []):
                error_messages.append(error)
        except AttributeError:  # Depending on the error, we may not get a dict, but only a string.
            error_messages.append(message)

        for error_message in error_messages:
            if duplicate_message in error_message:
                raise DuplicateObject(response)

def _create_object(session, api_host, resource_path, kwargs):
    """
    Create a new object in the API

    :param session: A session object to use to make the request
    :param api_host: The host where the API is located
    :param resource_path: The path where the objects are created
    :param kwargs: The arguments to use to create the object
    """
    headers = {"Content-Type": "application/json"}
    res = session.post(path_join(api_host, resource_path), headers=headers, data=json.dumps(kwargs))
    if res.status_code == 400:
        _test_for_duplicate(res)
    res.raise_for_status()
    return res.headers["location"]

def _update_object(session, api_host, obj):
    headers = {"Content-Type": "application/json"}
    res = session.patch(path_join(api_host, obj["resource_uri"]), headers=headers, data=json.dumps(obj))
    res.raise_for_status()

def _list_objects(session, api_host, resource_path, filters, _extend_list=None):
    """
    :param session: A session object to use to make the request
    :param api_host: The host where the API is located
    :param resource_path: The path where the objects are listed
    :param filters: Filters to apply to the request
    :return: The list of objects that are retrieved at  this endpoint
    :rtype: list
    """
    _extend_list = _extend_list if _extend_list is not None else []

    if resource_path is None:
        return _extend_list

    for kw in API_ONLY_KW:
        assert kw not in filters, "You can't use the {0} pagination keyword".format(kw) #TODO: Accept on the first hit

    filters = _clean_related_filters(filters)

    res = session.get(path_join(api_host, resource_path), params=filters)
    res.raise_for_status()
    content = res.json()
    _extend_list.extend(content["objects"])

    return _list_objects(session, api_host, content["meta"]["next"], filters, _extend_list)

