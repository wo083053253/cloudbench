#coding:utf-8
class BaseCloud(object):
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
        :rtype: dict
        """
        raise NotImplementedError()
