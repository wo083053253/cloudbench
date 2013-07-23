#coding:utf-8
import six

import boto.ec2

from stackbench.cloud import get_attachment_point
from stackbench.cloud.base import BaseCloud
from stackbench.cloud.factory import make_metadata_prop
from stackbench.cloud.exceptions import VolumeUnavailableError


def check_volume_attached(volume):
    if six.u(volume.status) != six.u("in-use"):
        raise VolumeUnavailableError(volume)


class EC2(BaseCloud):
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
        volumes = self.conn.get_all_volumes(filters={"attachment.instance-id": self._instance_id})
        for volume in volumes:
            check_volume_attached(volume)
        return dict((get_attachment_point(volume.attach_data.device), volume) for volume in volumes)
