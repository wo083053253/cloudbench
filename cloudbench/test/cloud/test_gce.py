#coding:utf-8
import unittest
import six

import requests

from cloudbench.cloud import GCE_ENDPOINT, EC2_ENDPOINT, Cloud
from cloudbench.cloud.exceptions import CloudAPIError
from cloudbench.test.cloud import MockPathExists

from cloudbench.test.utils import UnreachableTestAdapter, PredictableTestAdapter, RepeatingTestAdapter


class GCETestCase(unittest.TestCase):
    def setUp(self):
        self.session = requests.Session()
        self.session.mount(EC2_ENDPOINT, UnreachableTestAdapter())
        self.ec2_response = requests.Response()
        self.ec2_response.status_code = 200

    def test_metadata(self):
        # Instance type
        response1 = requests.Response()
        response1.status_code = 200
        response1._content = six.b("projects/1234/machineTypes/n1-standard-1-d")
        response1.encoding = "utf-8"

        # AZ
        response2 = requests.Response()
        response2.status_code = 200
        response2._content = six.b("projects/1234/zones/us-central1-b")
        response2.encoding = "utf-8"

        # Attachments
        response3 = requests.Response()
        response3.status_code = 200
        response3._content = six.b('[{"deviceName":"boot","index":0,"mode":"READ_WRITE","type":"EPHEMERAL"},{"deviceName":"ephemeral-disk-0","index":1,"mode":"READ_WRITE","type":"EPHEMERAL"},{"deviceName":"scalr-disk-1a043e80","index":2,"mode":"READ_WRITE","type":"PERSISTENT"}]')
        response3.encoding = "utf-8"


        adapter = PredictableTestAdapter([self.ec2_response, response1, response2, response2, response3])
        self.session.mount(GCE_ENDPOINT, adapter)

        cloud = Cloud(self.session)

        self.assertEqual("n1-standard-1-d", cloud.instance_type)
        self.assertEqual("us-central1-b", cloud.availability_zone)
        self.assertEqual("us-central1", cloud.location)
        self.assertEqual("GCE", cloud.provider)

        attachments = cloud.attachments

        with MockPathExists(["/dev/sda", "/dev/sdb", "/dev/sdc"]):
            self.assertSequenceEqual(["/dev/sda", "/dev/sdb", "/dev/sdc"],
                                     [attachment.device for attachment in attachments])

        self.assertSequenceEqual([False, False, True],
                                 [attachment.persistent for attachment in attachments])

        self.assertSequenceEqual(["GCE Disk"] * 3, [attachment.provider for attachment in attachments])

        self.assertEqual(0, len(adapter.responses))

    def test_error_propagation(self):
        response = requests.Response()
        response.status_code = 500
        adapter = RepeatingTestAdapter(response)

        self.session.mount(GCE_ENDPOINT, adapter)

        cloud = Cloud(self.session)

        self.assertRaises(CloudAPIError, getattr, cloud, "location")
