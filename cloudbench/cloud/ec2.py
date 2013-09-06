#coding:utf-8
import six

import boto.ec2

from cloudbench.cloud import find_attachment_point
from cloudbench.cloud.base import BaseCloud, BaseVolume
from cloudbench.cloud.factory import make_metadata_prop


def is_attached(volume):
    return volume.status == six.u("in-use")


class EC2Volume(BaseVolume):
    provider = "EBS"

    def __init__(self, volume):
        self._volume = volume

    @property
    def _cloud_device(self):
        return self._volume.attach_data.device

    @property
    def persistent(self):
        #TODO: We only return EBS volumes
        return True


class EC2(BaseCloud):
    provider = "EC2"

    metadata_server = "http://169.254.169.254/latest/meta-data"
    instance_type = make_metadata_prop("instance-type")
    availability_zone = make_metadata_prop("placement/availability-zone")
    _instance_id = make_metadata_prop("instance-id")
    _conn = None

    @property
    def conn(self):
        # Boto will find its credentials from the environment and raise an error if they're not there.
        if self._conn is None:
            self._conn = boto.ec2.connect_to_region(self.location)
        return self._conn

    @property
    def location(self):
        return self.availability_zone[:-1]

    @property
    def attachments(self):
        #TODO: This only returns EBS volumes
        volumes = self.conn.get_all_volumes(filters={"attachment.instance-id": self._instance_id})
        return [EC2Volume(volume) for volume in volumes if is_attached(volume)]
