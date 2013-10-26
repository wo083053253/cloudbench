#coding:utf-8
import unittest

from cloudbench.test.cloud import pyrax_importable
from cloudbench.test.cloud.rackspace_utils import MockPyrax, MockServer, MockFlavor, MockIncompleteVolume, MockActualVolume
from cloudbench.test.utils import MockSubprocessCall


@unittest.skipUnless(pyrax_importable, "pyrax is not importable")
class RackspaceTestCase(unittest.TestCase):
    def setUp(self):
        from cloudbench.cloud.rackspace import RackspaceOpenCloud
        self.pyrax = MockPyrax()

        self.cloud = RackspaceOpenCloud()
        self.cloud._conn = self.pyrax

    def test_instance_attributes(self):
        mock_server = MockServer("i123", 3)
        mock_flavor = MockFlavor("myflavor")

        self.pyrax.cloudservers.servers.servers["123.com"] = mock_server
        self.pyrax.cloudservers.flavors.flavors[3] = mock_flavor

        with MockSubprocessCall(0, "DFW"):
            self.assertEqual("DFW", self.cloud.location)

        with MockSubprocessCall(0, "123.com"):
            _ = self.cloud.instance  # Prime the cache

        self.assertEqual(mock_server, self.cloud.instance)
        self.assertEqual(mock_flavor.human_id, self.cloud.instance_type)

    def test_volumes(self):
        mock_server = MockServer("i123", 3)
        vol1 = MockIncompleteVolume("v1")
        vol2 = MockIncompleteVolume("v2")

        vol1_complete = MockActualVolume(100, [{'device': '/dev/xvdb', 'server_id': '', 'id': '', 'volume_id': ''}])
        vol2_complete = MockActualVolume(140, [{'device': '/dev/xvdc', 'server_id': '', 'id': '', 'volume_id': ''}])

        self.pyrax.cloudservers.servers.servers["123.com"] = mock_server
        self.pyrax.cloudservers.volumes.volumes["i123"] = [vol1, vol2]
        self.pyrax.cloud_blockstorage.volumes["v1"] = vol1_complete
        self.pyrax.cloud_blockstorage.volumes["v2"] = vol2_complete

        with MockSubprocessCall(0, "123.com"):
            _ = self.cloud.instance  # Prime the cache

        volumes = self.cloud.attachments
        self.assertEqual(2, len(volumes))

        vol1_loaded, vol2_loaded = volumes

        self.assertEqual("/dev/xvdb", vol1_loaded._cloud_device)
        self.assertEqual(100, vol1_loaded.size)
        self.assertEqual("/dev/xvdc", vol2_loaded._cloud_device)
        self.assertEqual(140, vol2_loaded.size)

