#coding:utf-8
import requests


def make_metadata_prop(path):
    def method(self):
        url = "/".join([self.metadata_server, path])
        res = requests.get(url)
        if res.status_code != 200:
            raise Exception("Unexpected response: {0}".format(res.status_code))
        return res.text
    return property(method)