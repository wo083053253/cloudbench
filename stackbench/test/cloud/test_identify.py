#coding:utf-8
import unittest
import requests

from stackbench.cloud import EC2_ENDPOINT, GCE_ENDPOINT, Cloud
from stackbench.cloud.exceptions import CloudUnavailableError

from stackbench.test.cloud import boto_importable
from stackbench.test.utils import RepeatingTestAdapter, UnreachableTestAdapter


class IdentifyCloudTestCase(unittest.TestCase):
    def setUp(self):
        self.session = requests.Session()

    @unittest.skipUnless(boto_importable, "boto is not importable")
    def test_ec2(self):
        response = requests.Response()
        response.status_code = 200
        adapter = RepeatingTestAdapter(response)

        self.session.mount(EC2_ENDPOINT, adapter)
        self.session.mount(GCE_ENDPOINT, UnreachableTestAdapter())

        cloud = Cloud(self.session)

        self.assertEqual("EC2", cloud.__class__.__name__)

    def test_gce(self):
        response = requests.Response()
        response.status_code = 200
        adapter = RepeatingTestAdapter(response)

        self.session.mount(GCE_ENDPOINT, adapter)
        self.session.mount(EC2_ENDPOINT, UnreachableTestAdapter())

        cloud = Cloud(self.session)

        self.assertEqual("GCE", cloud.__class__.__name__)

    def test_not_found(self):
        self.session.mount(EC2_ENDPOINT, UnreachableTestAdapter())
        self.session.mount(GCE_ENDPOINT, UnreachableTestAdapter())

        self.assertRaises(CloudUnavailableError, Cloud, self.session)
