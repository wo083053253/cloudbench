#coding:utf-8
import string
import subprocess
import json
import logging

from cloudbench.cloud import CloudUnavailableError
from cloudbench.cloud.base import BaseVolume, BaseMetadataServerCloud


logger = logging.getLogger(__name__)


GCE_DISK_PERSISTENT = "PERSISTENT"


class GCE(BaseMetadataServerCloud):
    provider = "GCE"

    metadata_server = "http://metadata/computeMetadata/v1beta1"

    @property
    def fq_instance_type(self):
        return self._get_metadata_path("instance/machine-type")

    @property
    def fq_availability_zone(self):
        return self._get_metadata_path("instance/zone")

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


def translate_attachment_point(index):
    return "/dev/sd{0}".format(string.ascii_lowercase[index])


class GCEVolume(BaseVolume):
    def __init__(self, vol_info):
        self._vol_info = vol_info

    @property
    def _cloud_device(self):
        return translate_attachment_point(self._vol_info["index"])

    @property
    def persistent(self):
        return self._vol_info["type"] == GCE_DISK_PERSISTENT

    @property
    def provider(self):
        return "GCE Disk" if self.persistent else "GCE Scratch"

    @property
    def size(self):
        #TODO: This is somewhat slow becasue we don't pass the project / zone
        name = self._vol_info["deviceName"]

        args = ["gcutil", "--format=json", "getdisk", name]
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.wait():
            raise CloudUnavailableError("Could not access volume info for %s" % name)
        stdout, stderr = proc.communicate()

        disk = json.loads(stdout)
        return int(disk["sizeGb"])


