#coding:utf-8
import os.path

from cloudbench.cloud.exceptions import VolumeNotFoundError, CloudUnavailableError


def find_attachment_point(device_path):
    if os.path.exists(device_path):
        return device_path
    xvd_path = device_path.replace("/dev/sd", "/dev/xvd")
    if os.path.exists(xvd_path):
        return xvd_path
    raise VolumeNotFoundError(device_path)


def import_by_name(class_path):
    module, klass = class_path.rsplit(".", 1)
    try:
        _mod = __import__(module, fromlist=[klass])
    except ImportError as e:
        raise CloudUnavailableError("Unable to import provider class {0}: {1}".format(class_path, e))
    else:
        return getattr(_mod, klass)