#coding:utf-8
import unittest

from cloudbench.cloud import find_attachment_point
from cloudbench.cloud.exceptions import VolumeNotFoundError

from cloudbench.test.utils import MockPathExists
from cloudbench.utils.freeze import freeze_dict, unfreeze_dict


class UtilTestCase(unittest.TestCase):
    def test_find_attachment(self):
        with MockPathExists(["/dev/sda", "/dev/xvdg"]):
            self.assertEqual("/dev/sda", find_attachment_point("/dev/sda"))
            self.assertEqual("/dev/xvdg", find_attachment_point("/dev/sdg"))
            self.assertRaises(VolumeNotFoundError, find_attachment_point, "/dev/sdb")


class FreezeTestCase(unittest.TestCase):
    def test_freeze(self):
        test_dict = {"a": "b", "c": {"d": "e"}, "f": {"g": {"h": "i"}}}
        self.assertEqual(test_dict, unfreeze_dict(freeze_dict(test_dict)))
