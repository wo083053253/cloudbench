#coding:utf-8
import unittest

import requests

from cloudbench.cloud import Cloud
from cloudbench.cloud.exceptions import CloudUnavailableError

from cloudbench.test.cloud import boto_importable, pyrax_importable
from cloudbench.test.utils import RepeatingTestAdapter, UnreachableTestAdapter, MockSession, MockSubprocessCall


class IdentifyCloudTestCase(unittest.TestCase):
    def setUp(self):
        self.session = requests.Session()

    @unittest.skipUnless(boto_importable, "boto is not importable")
    def test_ec2(self):
        response = requests.Response()
        response.status_code = 200
        adapter = RepeatingTestAdapter(response)

        self.session.mount("http://169.254.169.254", adapter)
        self.session.mount("http://metadata", UnreachableTestAdapter())

        with MockSession(self.session), MockSubprocessCall(0, "Not Rackspace"):
            cloud = Cloud()

        self.assertEqual("EC2", cloud.__class__.__name__)

    @unittest.skipUnless(pyrax_importable, "pyrax is not importable")
    def test_rackspace(self):
        self.session.mount("http://169.254.169.254", UnreachableTestAdapter())
        self.session.mount("http://metadata", UnreachableTestAdapter())

        with MockSession(self.session), MockSubprocessCall(0, "Rackspace"):
            cloud = Cloud()

        self.assertEqual("RackspaceOpenCloud", cloud.__class__.__name__)

    def test_gce(self):
        response = requests.Response()
        response.status_code = 200
        adapter = RepeatingTestAdapter(response)

        self.session.mount("http://metadata", adapter)
        self.session.mount("http://169.254.169.254", UnreachableTestAdapter())

        with MockSession(self.session), MockSubprocessCall(0, "Not Rackspace"):
            cloud = Cloud()

        self.assertEqual("GCE", cloud.__class__.__name__)

    def test_not_found(self):
        self.session.mount("http://169.254.169.254", UnreachableTestAdapter())
        self.session.mount("http://metadata", UnreachableTestAdapter())

        with MockSession(self.session), MockSubprocessCall(0, "Not Rackspace"):
            self.assertRaises(CloudUnavailableError, Cloud)

        with MockSession(self.session), MockSubprocessCall(1, "Rackspace"):
            self.assertRaises(CloudUnavailableError, Cloud)
