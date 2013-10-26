#coding:utf-8
import requests

from cloudbench.cloud.utils import import_by_name
from cloudbench.cloud.exceptions import VolumeNotFoundError, CloudUnavailableError


PROVIDERS = [
    "cloudbench.cloud.ec2.EC2",
    "cloudbench.cloud.gce.GCE",
    "cloudbench.cloud.rackspace.RackspaceOpenCloud",
]


def _find_provider(providers_class_paths):
    for provider_class_path in providers_class_paths:
        try:
            provider_cls = import_by_name(provider_class_path)
        except CloudUnavailableError:
            continue

        if provider_cls.is_present():
            return provider_cls

    raise CloudUnavailableError("Tried: {0}".format(", ".join(providers_class_paths)))


def Cloud():
    """
    Retrieve an instance of the cloud you're running in
    :param session: Session to use for HTTP requests
    :type session: requests.sessions.Session
    :returns: A Cloud instance corresponding to the platform the instance is running on
    :rtype: cloudbench.cloud.base.BaseCloud
    """
    ProviderClass = _find_provider(PROVIDERS)
    return ProviderClass()

