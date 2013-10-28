#coding:utf-8
import six

import boto.ec2

from cloudbench.cloud.base import BaseVolume, BaseMetadataServerCloud


class EC2(BaseMetadataServerCloud):
    provider = "EC2"

    metadata_server = "http://169.254.169.254/latest/meta-data"

    def __init__(self):
        super(EC2, self).__init__()
        self._conn = None

    @property
    def instance_type(self):
        return self._get_metadata_path("instance-type")

    @property
    def availability_zone(self):
        return self._get_metadata_path("placement/availability-zone")

    @property
    def _instance_id(self):
        return self._get_metadata_path("instance-id")

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

    @property
    def size(self):
        return self._volume.size

    def _get_extra_assets(self):
        if self._volume.iops is not None:
            return ["{0} PIOPS".format(self._volume.iops)]
        return []
