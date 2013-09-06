#coding:utf-8
import os.path
import requests

from cloudbench.cloud.exceptions import VolumeNotFoundError, CloudUnavailableError


GCE_ENDPOINT = "http://metadata"
EC2_ENDPOINT = "http://169.254.169.254"

METADATA_SERVERS = {
    "GCE": GCE_ENDPOINT,
    "EC2": EC2_ENDPOINT,
}

PROVIDER_CLASSES = {
    "GCE": "cloudbench.cloud.gce.GCE",
    "EC2": "cloudbench.cloud.ec2.EC2"
}


def find_attachment_point(device_path):
    if os.path.exists(device_path):
        return device_path
    xvd_path = device_path.replace("/dev/sd", "/dev/xvd")
    if os.path.exists(xvd_path):
        return xvd_path
    raise VolumeNotFoundError(device_path)


def _get_provider(session, timeout=1):
    for name, metadata_server in METADATA_SERVERS.items():
        try:
            session.get(metadata_server, timeout=timeout)
        except requests.ConnectionError:
            continue
        else:
            return name
    raise CloudUnavailableError("Tried: {0}".format(", ".join(METADATA_SERVERS.keys())))


def _get_provider_class(path):
    module, klass = path.rsplit(".", 1)
    try:
        _mod = __import__(module, fromlist=[klass])
    except ImportError as e:
        raise CloudUnavailableError("Unable to import provider class {0}: {1}".format(path, e))
    else:
        return getattr(_mod, klass)


def Cloud(session=None):
    """
    Retrieve an instance of the cloud you're running in
    :param session: Session to use for HTTP requests
    :type session: requests.sessions.Session
    :returns: A Cloud instance corresponding to the platform the instance is running on
    :rtype: cloudbench.cloud.base.BaseCloud
    """
    if session is None:
        session = requests.Session()
    provider_name = _get_provider(session)
    provider = _get_provider_class(PROVIDER_CLASSES[provider_name])
    return provider(session)

