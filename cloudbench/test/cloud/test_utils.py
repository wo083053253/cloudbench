#coding:utf-8
import unittest

from cloudbench.cloud.exceptions import VolumeNotFoundError
from cloudbench.cloud.utils import find_attachment_point

from cloudbench.test.utils import MockPathExists


class UtilTestCase(unittest.TestCase):
    def test_find_attachment(self):
        with MockPathExists(["/dev/sda", "/dev/xvdg"]):
            self.assertEqual("/dev/sda", find_attachment_point("/dev/sda"))
            self.assertEqual("/dev/xvdg", find_attachment_point("/dev/sdg"))
            self.assertRaises(VolumeNotFoundError, find_attachment_point, "/dev/sdb")
