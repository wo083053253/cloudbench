#coding:utf-8
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
        :rtype: dict
        """
        raise NotImplementedError()
