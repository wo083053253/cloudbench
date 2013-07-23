#coding:utf-8
import string

from stackbench.cloud import find_attachment_point
from stackbench.cloud.base import BaseCloud
from stackbench.cloud.factory import make_metadata_prop


GCE_DISK_PERSISTENT = "PERSISTENT"


def translate_attachment_point(disk):
    return "/dev/sd{0}".format(string.ascii_lowercase[disk["index"]])



class GCE(BaseCloud):
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
        disks = res.json()
        return dict((find_attachment_point(translate_attachment_point(disk)), disk) for disk in disks if disk["type"] == GCE_DISK_PERSISTENT)

