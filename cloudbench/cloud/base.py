#coding:utf-8
from cloudbench.cloud import find_attachment_point


class BaseCloud(object):
    def __init__(self, session):
        """
        :param session:
        :type session: requests.sessions.Session
        """
        self.session = session

    @property
    def metadata_server(self):
        """
        :rtype: str
        """
        raise NotImplementedError()

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

    def __repr__(self):
        return "<{0}>".format(self.__class__.__name__)


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

    def __repr__(self):
        return "<{0}: {1} ({2})>".format(self.__class__.__name__, self.device, "P" if self.persistent else "E")
