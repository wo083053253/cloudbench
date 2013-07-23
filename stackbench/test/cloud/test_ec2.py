#coding:utf-8
import six
import unittest

import requests

from stackbench.cloud import Cloud, GCE_ENDPOINT, EC2_ENDPOINT

from stackbench.test.cloud import boto_importable, MockPathExists
from stackbench.test.utils import UnreachableTestAdapter, PredictableTestAdapter, RepeatingTestAdapter


@unittest.skipUnless(boto_importable, "boto is not importable")
class EC2TestCase(unittest.TestCase):
    def setUp(self):
        from boto.ec2.volume import Volume, AttachmentSet
        self.Volume = Volume
        self.AttachmentSet = AttachmentSet

        self.session = requests.Session()
        self.session.mount(GCE_ENDPOINT, UnreachableTestAdapter())
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


        adapter = PredictableTestAdapter([self.ec2_response, response1, response2, response2])
        self.session.mount(EC2_ENDPOINT, adapter)

        cloud = Cloud(self.session)

        self.assertEqual("m1.large", cloud.instance_type)
        self.assertEqual("us-east-1a", cloud.availability_zone)
        self.assertEqual("us-east-1", cloud.location)
        self.assertEqual(0, len(adapter.responses))

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

        volume2 = self.Volume()
        volume2.attach_data = self.AttachmentSet()
        volume2.attach_data.device = "/dev/sda"
        volume2.status = "in-use"

        volume3 = self.Volume()
        volume3.status = "attaching"

        volumes = [volume1, volume2, volume3]

        self.ec2_response._content = "i-1234"
        adapter = RepeatingTestAdapter(self.ec2_response)
        self.session.mount(EC2_ENDPOINT, adapter)
        cloud = Cloud(self.session)
        cloud._conn = MockConn(volumes)

        with MockPathExists(["/dev/sda", "/dev/xvdg"]):
            attachments = cloud.attachments

        self.assertItemsEqual(["/dev/xvdg", "/dev/sda"], attachments.keys())

        self.assertEqual(volume1, attachments["/dev/xvdg"])
        self.assertEqual(volume2, attachments["/dev/sda"])

        self.assertEqual(1, len(cloud._conn.requests))
        self.assertDictEqual({"attachment.instance-id":"i-1234"}, cloud._conn.requests[0])
