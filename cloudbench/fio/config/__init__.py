#coding:utf-8
DEFAULT_MODE = "read"
READ_MODES = ["read", "randread", "rw", "readwrite", "randrw"]
WRITE_MODES = ["write", "randwrite", "rw", "readwrite", "randrw"]

DEFAULT_BLOCK_SIZE = "4k"

DEFAULT_IO_DEPTH = 1


class ConfigInterface(object):
    def to_ini(self):
        raise NotImplementedError()
