#coding:utf-8
import os
import subprocess

import pyrax

from cloudbench.cloud import CloudUnavailableError
from cloudbench.cloud.base import BaseCloud, BaseVolume


def get_xenstore_key(key):
    args = ["/usr/bin/xenstore-read", key]
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.wait():
        raise CloudUnavailableError("Could not access xenstore")
    stdout, stderr = proc.communicate()
    return stdout.decode("utf-8").strip()


def make_xenstore_getter(key):
    def method(self):
        return get_xenstore_key(key)
    return method


class RackspaceOpenCloud(BaseCloud):
    provider = "Rackspace"

    def __init__(self):
        self._conn = None
        self._instance = None

    location = property(make_xenstore_getter("vm-data/provider_data/region"))

    _hostname = property(make_xenstore_getter("vm-data/hostname"))

    @property
    def instance(self):
        if self._instance is None:
            instance = self._conn.cloudservers.servers.find(name=self._hostname)
            self._instance = instance
        return self._instance

    @property
    def conn(self):
        if self._conn is None:
            pyrax.set_setting("identity_type", "rackspace")
            pyrax.set_credentials(os.environ["RACKSPACE_USERNAME"], os.environ["RACKSPACE_API_KEY"])
            pyrax.set_setting("verify_ssl", False)
            self._conn = pyrax  # We love globals, don't we?!
        return self._conn

    @property
    def instance_type(self):
        flavor_id = self.instance.flavor["id"]
        flavor = self.conn.cloudservers.flavors.get(flavor_id)
        return flavor.human_id

    @property
    def attachments(self):
        instance_volumes = self.conn.cloudservers.volumes.get_server_volumes(self.instance.id)
        return [RackspaceOpenCloudVolume(self.conn.cloud_blockstorage.get(volume.id)) for volume in instance_volumes]

    @classmethod
    def is_present(cls):
        try:
            provider = get_xenstore_key("vm-data/provider_data/provider")
        except CloudUnavailableError:
            return False
        return provider == cls.provider


class RackspaceOpenCloudVolume(BaseVolume):
    provider = "RackspaceCinder"

    def __init__(self, volume):
        """
        :type volume: :class:`pyrax.cloudblockstorage.CloudBlockStorageVolume`
        """
        self._volume = volume

    @property
    def _cloud_device(self):
        assert len(self._volume.attachments) == 1, "Volume is attached to multiple instances!"
        attachment, = self._volume.attachments
        return attachment["device"]

    @property
    def persistent(self):
        return True  #TODO: Report instance volumes?

    @property
    def size(self):
        return self._volume.size