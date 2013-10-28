#coding:utf-8
import requests
from cloudbench.cloud.exceptions import CloudAPIError

from cloudbench.cloud.utils import find_attachment_point


class BaseCloud(object):
    @property
    def instance_type(self):
        """
        :rtype: str
        """
        raise NotImplementedError()

    @property
    def availability_zone(self):
        """
        :rtype: str
        """
        raise NotImplementedError()

    @property
    def location(self):
        """
        :rtype: str
        """
        raise NotImplementedError()

    @property
    def attachments(self):
        """
        :rtype: list of BaseVolume
        """
        raise NotImplementedError()

    @property
    def provider(self):
        """
        The provider for this Cloud

        :rtype: str
        """
        raise NotImplementedError()

    @classmethod
    def is_present(cls):
        raise NotImplementedError()

    def __repr__(self):
        return "<{0}>".format(self.__class__.__name__)


class BaseMetadataServerCloud(BaseCloud):
    def __init__(self):
        self.session = requests.Session()

    @property
    def metadata_server(self):
        """
        :rtype: str
        """
        raise NotImplementedError()

    def _get_metadata_path(self, path):
        url = "/".join([self.metadata_server, path])
        res = self.session.get(url)
        if res.status_code != 200:
            raise CloudAPIError(res)
        return res.text

    @classmethod
    def is_present(cls):
        try:
            session = requests.Session()
            res = session.get(cls.metadata_server, timeout=1)
            res.raise_for_status()
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError) as e:
            return False
        return True


class BaseVolume(object):
    @property
    def device(self):
        """
        The device where the volume is found on the filesystem.

        :rtype: str
        """
        return find_attachment_point(self._cloud_device)

    @property
    def _cloud_device(self):
        """
        The device as reported by the Cloud.

        :rtype: str
        """
        raise NotImplementedError()

    @property
    def persistent(self):
        """
        Whether this volume is persistent.

        :rtype: bool
        """
        raise NotImplementedError()

    @property
    def provider(self):
        """
        The provider for this Volume

        :rtype: str
        """
        raise NotImplementedError()

    @property
    def size(self):
        """
        The size for this Volume

        :rtype: int
        """
        raise NotImplementedError()

    def _get_extra_assets(self):
        """
        Extra assets for this Volume (on top of provider and size)

        :rtype: list of str
        """
        return []

    @property
    def assets(self):
        """
        The list of assets for this Volume

        :rtype: list of str
        """  #TODO: Provider maybe should depend on whether we are persistent here.
        output = [self.provider, "{0} GB".format(self.size)]
        output.extend(self._get_extra_assets())
        return output

    def __repr__(self):
        return "<{0}: {1} ({2})>".format(self.__class__.__name__, self.device, "P" if self.persistent else "E")
