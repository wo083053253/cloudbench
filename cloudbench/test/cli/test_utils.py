#coding:utf-8
import unittest

from cloudbench.cli import may_bench, identify_benchmark_volumes
from cloudbench.utils.freeze import unfreeze_dict, freeze_dict
from cloudbench.utils.math import block_size_in_kb, InvalidBlockSize

from cloudbench.test.cli.utils import TestVolume, TestCloud
from cloudbench.test.utils import MockCheckFilename


class CLITestCase(unittest.TestCase):
    def test_may_bench(self):
        self.assertFalse(may_bench(["/dev/sda", "/dev/xvda"], "/dev/sda"))
        self.assertTrue(may_bench(["/dev/sda", "/dev/xvda"], "/dev/sdb"))

    def test_identify_benchmark_volumes(self):
        vol1 = TestVolume("/dev/sda", False, "TestProvider", 10)
        vol2 = TestVolume("/dev/sdb", True, "TestProvider", 15)
        vol3 = TestVolume("/dev/sdc", True, "TestProvider", 15)
        vol4 = TestVolume("/dev/sdd", True, "TestProvider", 20)

        cloud = TestCloud("Cloud", "m.test", "loc/1", "loc", [vol1, vol2, vol3, vol4])
        nobench = ["/dev/sdb", "/dev/xvdb"]


        with MockCheckFilename(["/dev/sda", "/dev/sdb", "/dev/sdc", "/dev/sdd"]):
            vols = identify_benchmark_volumes(cloud, nobench)

        self.assertEqual([vol3, vol4], vols)


class FreezeTestCase(unittest.TestCase):
    def test_freeze(self):
        test_dict = {"a": "b", "c": {"d": "e"}, "f": {"g": {"h": "i"}}}
        self.assertEqual(test_dict, unfreeze_dict(freeze_dict(test_dict)))


class UnitTestCase(unittest.TestCase):
    def test_units(self):
        self.assertEqual(10, block_size_in_kb("10k"))
        self.assertEqual(10, block_size_in_kb("10kb"))
        self.assertEqual(10240, block_size_in_kb("10m"))
        self.assertEqual(10240, block_size_in_kb("10mb"))

        self.assertEqual(10, block_size_in_kb("10K"))
        self.assertEqual(10, block_size_in_kb("10KB"))
        self.assertEqual(10240, block_size_in_kb("10M"))
        self.assertEqual(10240, block_size_in_kb("10MB"))

        self.assertRaises(InvalidBlockSize, block_size_in_kb, "1")
        self.assertRaises(InvalidBlockSize, block_size_in_kb, "10ZB")
