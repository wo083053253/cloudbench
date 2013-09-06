#coding:utf-8
import string

from cloudbench.cloud import find_attachment_point
from cloudbench.cloud.base import BaseCloud, BaseVolume
from cloudbench.cloud.factory import make_metadata_prop


GCE_DISK_PERSISTENT = "PERSISTENT"


def translate_attachment_point(index):
    return "/dev/sd{0}".format(string.ascii_lowercase[index])


class GCEVolume(BaseVolume):
    provider = "GCE Disk"

    def __init__(self, vol_info):
        self._vol_info = vol_info

    @property
    def _cloud_device(self):
        return translate_attachment_point(self._vol_info["index"])

    @property
    def persistent(self):
        return self._vol_info["type"] == GCE_DISK_PERSISTENT


class GCE(BaseCloud):
    provider = "GCE"

    metadata_server = "http://metadata/computeMetadata/v1beta1"
    fq_instance_type = make_metadata_prop("instance/machine-type")
    fq_availability_zone = make_metadata_prop("instance/zone")

    @property
    def instance_type(self):
        return self.fq_instance_type.rsplit("/", 1)[1]

    @property
    def availability_zone(self):
        return self.fq_availability_zone.rsplit("/", 1)[1]

    @property
    def location(self):
        return self.availability_zone[:-2]

    @property
    def attachments(self):
        url = "/".join([self.metadata_server, "instance", "disks/",]) + "?recursive=true"
        res = self.session.get(url)
        volumes_info = res.json()
        return [GCEVolume(vol_info) for vol_info in volumes_info]

