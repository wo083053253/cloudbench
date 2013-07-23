#coding:utf-8
import requests


METADATA_SERVERS = {
    "GCE": "http://metadata/computeMetadata/v1beta1",
    "EC2": "http://169.254.169.254/latest/meta-data"
}

PROVIDER_CLASSES = {}


def Cloud(*args, **kwargs):
    """
    Retrieve an instance of the cloud you're running in
    :rtype: stackbench.cloud.base.BaseCloud
    """
    provider = get_provider()
    return PROVIDER_CLASSES[provider](*args, **kwargs)


def get_provider(timeout=1):
    for name, metadata_server in METADATA_SERVERS.items():
        try:
            requests.get(metadata_server, timeout=timeout)
        except requests.ConnectionError:
            continue
        else:
            return name
    raise Exception("Unknown Cloud (tried: {0})".format(", ".join(METADATA_SERVERS.keys())))


from stackbench.cloud.ec2 import EC2
from stackbench.cloud.gce import GCE

PROVIDER_CLASSES.update({
    "GCE": GCE,
    "EC2": EC2
})
