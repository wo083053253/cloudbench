#coding:utf-8
import six
import unittest

import requests

from cloudbench.cloud import Cloud

from cloudbench.test.cloud import boto_importable
from cloudbench.test.utils import UnreachableTestAdapter, PredictableTestAdapter, RepeatingTestAdapter, MockPathExists, MockSession


@unittest.skipUnless(boto_importable, "boto is not importable")
class EC2TestCase(unittest.TestCase):
    def setUp(self):
        from boto.ec2.volume import Volume, AttachmentSet
        self.Volume = Volume
        self.AttachmentSet = AttachmentSet

        self.session = requests.Session()
        self.session.mount("http://metadata", UnreachableTestAdapter())
        self.ec2_response = requests.Response()
        self.ec2_response.status_code = 200

    def test_metadata(self):
        # Instance type
        response1 = requests.Response()
        response1.status_code = 200
        response1._content = six.b("m1.large")
        response1.encoding = "utf-8"

        # AZ
        response2 = requests.Response()
        response2.status_code = 200
        response2._content = six.b("us-east-1a")
        response2.encoding = "utf-8"
        # TODO: Add instance ID, and test request paths.

        adapter = PredictableTestAdapter([self.ec2_response, response1, response2, response2])
        self.session.mount("http://169.254.169.254", adapter)

        with MockSession(self.session):
            cloud = Cloud()

        self.assertEqual("m1.large", cloud.instance_type)
        self.assertEqual("us-east-1a", cloud.availability_zone)
        self.assertEqual("us-east-1", cloud.location)
        self.assertEqual(0, len(adapter.responses))
        self.assertEqual("EC2", cloud.provider)

    def test_attachments(self):
        """
        Test that the attachments are:
            - Filtered
            - Returned with the correct mountpoint
        """
        class MockConn(object):
            def __init__(self, volumes):
                self.requests = []
                self.volumes = volumes

            def get_all_volumes(self, filters):
                self.requests.append(filters)
                return self.volumes

        volume1 = self.Volume()
        volume1.attach_data = self.AttachmentSet()
        volume1.status = "in-use"
        volume1.attach_data.device = "/dev/sdg"
        volume1.size = 10

        volume2 = self.Volume()
        volume2.attach_data = self.AttachmentSet()
        volume2.attach_data.device = "/dev/sda"
        volume2.status = "in-use"
        volume2.size = 100
        volume2.iops = 100

        volume3 = self.Volume()
        volume3.status = "attaching"
        volume3.attach_data = self.AttachmentSet()
        volume3.size = 15

        volumes = [volume1, volume2, volume3]

        self.ec2_response._content = "i-1234"
        adapter = RepeatingTestAdapter(self.ec2_response)
        self.session.mount("http://169.254.169.254", adapter)

        with MockSession(self.session):
            cloud = Cloud()

        cloud._conn = MockConn(volumes)

        attachments = cloud.attachments

        with MockPathExists(["/dev/sda", "/dev/xvdg"]):
            self.assertItemsEqual(["/dev/xvdg", "/dev/sda"], [attachment.device for attachment in attachments])

        self.assertEqual([True, True], [attachment.persistent for attachment in attachments])

        self.assertEqual(1, len(cloud._conn.requests))
        self.assertDictEqual({"attachment.instance-id":"i-1234"}, cloud._conn.requests[0])
        self.assertSequenceEqual(
            [["EBS", "10 GB"], ["EBS", "100 GB", "100 PIOPS"]],
            [attachment.assets for attachment in attachments]
        )
