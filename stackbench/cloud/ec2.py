#coding:utf-8
import os.path

import boto.ec2

from stackbench.cloud.base import BaseCloud
from stackbench.cloud.factory import make_metadata_prop


def get_attachment_point(volume):
    status = volume.status
    assert status == u"in-use", "Can't get attachment point for a non-attached volume!"
    device_path = volume.attach_data.device
    if os.path.exists(device_path):
        return device_path
    xvd_path = device_path.replace("/dev/sd", "/dev/xvd")
    if os.path.exists(xvd_path):
        return xvd_path
    raise Exception("Could not find attachment point for {0}".format(device_path))


class EC2(BaseCloud):
    metadata_server = "http://169.254.169.254/latest/meta-data"
    instance_type = make_metadata_prop("instance-type")
    availability_zone = make_metadata_prop("placement/availability-zone")

    _instance_id = make_metadata_prop("instance-id")

    @property
    def location(self):
        return self.availability_zone[:-1]

    @property
    def attachments(self):
        # Boto will find its credentials from the environment and raise an error if they're not there.
        conn = boto.ec2.connect_to_region(self.location)
        print "Instance ID", self._instance_id
        volumes = conn.get_all_volumes(filters={"attachment.instance-id": self._instance_id})
        return dict((get_attachment_point(volume), volume) for volume in volumes)
