#coding:utf-8
import requests

METADATA_SERVERS = {
    "GCE": "http://metadata/computeMetadata/v1beta1",
    "EC2": "http://169.254.169.254/latest/meta-data"
}

INSTANCE_TYPE_PATH = {
    "GCE": "instance/machine-type",
    "EC2": "instance-type"
}

AVAILABILITY_ZONE_PATH = {
    "GCE": "zone",
    "EC2": "placement/availability-zone"
}


class Cloud(object):
    _timeout = 1

    def __init__(self):
        self._provider = None
        self._instance_type = None
        self._availability_zone = None

    @property
    def provider(self):
        if self._provider is None:
            for name, metadata_server in METADATA_SERVERS.items():
                try:
                    requests.get(metadata_server, timeout=self._timeout)
                except requests.ConnectionError:
                    continue
                else:
                    self._provider = name
            assert self._provider is not None, "Unknown Cloud"
        return self._provider

    @property
    def _metadata_server(self):
        return METADATA_SERVERS[self.provider]

    @property
    def instance_type(self):
        if self._instance_type is None:
            path = INSTANCE_TYPE_PATH[self.provider]  #TODO: Catch errors? Probably not useful.
            res = requests.get("/".join([self._metadata_server, path]))
            self._instance_type = res.text
        return self._instance_type


    @property
    def availability_zone(self):
        if self._availability_zone is None:
            path = AVAILABILITY_ZONE_PATH[self.provider]
            res = requests.get("/".join([self._metadata_server, path]))
            self._availability_zone = res.text
        return self._availability_zone

    @property
    def location(self):
        #TODO: Kind of hackish, works for the moment
        return self.availability_zone[:-1]
