#coding:utf-8
import requests


METADATA_SERVERS = {
    "GCE": "http://metadata",
    "EC2": "http://169.254.169.254"
}

PROVIDER_CLASSES = {
    "GCE": "stackbench.cloud.gce.GCE",
    "EC2": "stackbench.cloud.ec2.EC2"
}


def get_provider(timeout=1):
    for name, metadata_server in METADATA_SERVERS.items():
        try:
            requests.get(metadata_server, timeout=timeout)
        except requests.ConnectionError:
            continue
        else:
            return name
    raise Exception("Unknown Cloud (tried: {0})".format(", ".join(METADATA_SERVERS.keys())))


def get_provider_class(path):
    module, klass = path.rsplit(".", 1)
    try:
        _mod = __import__(module, fromlist=[klass])
    except ImportError as e:
        raise Exception("Unable to import provider class {0}: {1}".format(path, e))
    else:
        return getattr(_mod, klass)



def Cloud(*args, **kwargs):
    """
    Retrieve an instance of the cloud you're running in
    :rtype: stackbench.cloud.base.BaseCloud
    """
    provider_name = get_provider()
    provider = get_provider_class(PROVIDER_CLASSES[provider_name])
    return provider(*args, **kwargs)

