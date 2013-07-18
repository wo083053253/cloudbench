#coding:utf-8
import requests

METADATA_INSTANCE_TYPE = [
    "http://metadata/computeMetadata/v1beta1/instance/machine-type",  # GCE
    "http://169.254.169.254/latest/meta-data/instance-type",  # EC2
]

def get_instance_type(timeout=1):
    """
    Guess the instance type by acessing the metadata endpoints
    """
    for endpoint in METADATA_INSTANCE_TYPE:
        try:
            res = requests.get(endpoint, timeout=timeout)
            return res.text
        except requests.ConnectionError:
            continue

    raise Exception("Unknown Cloud")
