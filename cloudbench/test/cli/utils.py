#coding:utf-8
import copy
from cloudbench.cloud.base import BaseVolume, BaseCloud
from cloudbench.utils.freeze import freeze_dict


class TestVolume(BaseVolume):
    def __init__(self, device, persistent, provider, size):
        self._device = device
        self._persistent = persistent
        self._provider = provider
        self._size = size

    @property
    def device(self):
        return self._device

    @property
    def persistent(self):
        return self._persistent

    @property
    def provider(self):
        return self._provider

    @property
    def size(self):
        return self._size


class TestCloud(BaseCloud):
    def __init__(self, provider, instance_type, az, location, attachments):
        self._provider = provider
        self._instance_type = instance_type
        self._az = az
        self._location = location
        self._attachments = attachments

    @property
    def provider(self):
        return self._provider

    @property
    def instance_type(self):
        return self._instance_type

    @property
    def availability_zone(self):
        return self._az

    @property
    def location(self):
        return self._location

    @property
    def attachments(self):
        return self._attachments


class TestAPIResource(object):
    def __init__(self):
        self.objects = {}

    def _from_objects(self, key):
        return copy.deepcopy(self.objects[key])

    def create(self, **kwargs):
        key = freeze_dict(kwargs)
        self.objects[key] = kwargs
        return self._from_objects(key)

    def get_or_create(self, **kwargs):
        key = freeze_dict(kwargs)
        if key not in self.objects:
            return self.create(**kwargs)
        return self._from_objects(key)


class TestAPIClient(object):
    """
    A dummy API to test that the correct objects are being passed around
    """
    def __init__(self):
        self.providers = TestAPIResource()
        self.locations = TestAPIResource()
        self.abstract_assets = TestAPIResource()
        self.physical_assets = TestAPIResource()
        self.configurations = TestAPIResource()
        self.measurements = TestAPIResource()
        self.measurement_assets = TestAPIResource()

        self.updates = []

    def update(self, obj):
        self.updates.append(obj)


class TestJobReport(object):
    def __init__(self):
        self.avg_iops = "iops"
        self.avg_lat = "lat"
        self.stddev_lat = "lat sd"
        self.avg_bw = "bw"
        self.stddev_bw = "bw sd"
