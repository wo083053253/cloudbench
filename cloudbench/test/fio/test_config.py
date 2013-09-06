#coding:utf-8
import unittest
import collections
from cloudbench.fio.config.config import FIOConfig

from cloudbench.fio.config.job import Job


class JobTestCase(unittest.TestCase):
    def test_mode(self):
        """
        Test that the correct mode is reported for jobs
        """
        j1 = Job({"rw":"read"})
        self.assertTrue(j1.is_read)
        self.assertFalse(j1.is_write)

        j2 = Job({"readwrite":"randwrite"})
        self.assertFalse(j2.is_read)
        self.assertTrue(j2.is_write)

        j3 = Job({"readwrite":"rw"})
        self.assertTrue(j3.is_read)
        self.assertTrue(j3.is_write)

        j4 = Job({"readwrite":"randwrite"})
        self.assertFalse(j4.is_read)
        self.assertTrue(j4.is_write)

    def test_bs(self):
        """
        Test that we report the correct block size
        """
        #TODO: What if we declare two vars?
        j1 = Job({"bs": "8k"})
        self.assertEqual("8k", j1.block_size)
        j2 = Job({"blocksize": "16k"})
        self.assertEqual("16k", j2.block_size)
        j3 = Job()
        self.assertEqual("4k", j3.block_size)

    def test_ini(self):
        """
        Test that we use a valid ini format (no spaces, allows None)
        """
        j = Job(collections.OrderedDict((("bs", "8k"), ("iodepth", 2), ("stonewall", None))))
        j.name = "my-job"
        self.assertEqual("[my-job]\nbs=8k\niodepth=2\nstonewall", j.to_ini().strip())

    def test_addition(self):
        """
        Test that when adding jobs, we
          - Create an anonymous job
          - Prioritize the right operand
        """
        j0 = Job({"bs": "4k", "iodepth": "4"}, "global")
        j1 = Job({"bs": "8k", "rw": "read"}, "job")

        j2 = j0 + j1

        self.assertEqual("anonymous", j2.name)
        self.assertEqual("read", j2.mode)
        self.assertEqual("8k", j2.block_size)
        self.assertEqual("4", j2.io_depth)

class CompositeConfigTestCase(unittest.TestCase):
    def test_ini(self):
        """
        Check that the composite config aggregates jobs, and in the correct order
        """
        j1 = Job({"engine":"libaio"}, "global")
        j2 = Job({"iodepth":4})

        c = FIOConfig()
        c.add_job(j1)
        c.add_job(j2)

        self.assertEqual("[global]\nengine=libaio\n\n\n[anonymous]\niodepth=4", c.to_ini().strip())