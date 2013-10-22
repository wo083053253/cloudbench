#coding:utf-8
import subprocess

from cloudbench.cloud.base import BaseCloud


def get_xenstore_key(key):
    args = ["/usr/bin/xenstore-read", key]
    return subprocess.check_output(args).decode("utf-8")


def make_xenstore_property(key):
    def method(self):
        return get_xenstore_key(key)
    return method


class RackspaceOpenCloud(BaseCloud):
    provider = "Rackspace"
    location = make_xenstore_property("vm-data/provider_data/region")

    @classmethod
    def is_present(cls):
        try:
            provider = get_xenstore_key("vm-data/provider_data/provider")
        except OSError:
            return False
        return provider == cls.provider

