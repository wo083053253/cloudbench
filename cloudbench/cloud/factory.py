#coding:utf-8
from cloudbench.cloud.exceptions import CloudAPIError


def make_metadata_prop(path):
    def method(self):
        url = "/".join([self.metadata_server, path])
        res = self.session.get(url)
        if res.status_code != 200:
            raise CloudAPIError(res)
        return res.text
    return property(method)