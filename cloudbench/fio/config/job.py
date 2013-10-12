#coding:utf-8
import io
from six.moves import configparser
import six

from cloudbench.fio.config import DEFAULT_MODE, READ_MODES, WRITE_MODES, DEFAULT_BLOCK_SIZE, DEFAULT_IO_DEPTH, ConfigInterface


ANONYMOUS_JOB = "anonymous"
GLOBAL_NAME = "global"  # Not exactly a job!


def to_option(value):
    """
    Normalizes an option for outputting to a config file.
    """
    if value is None:
        return value
    return str(value)


def make_mode_prop(accepted_modes):
    """
    Returns a property to identify whether the Job's mode is in the accepted modes.
    """
    def mode_prop(self):
        return self.mode in accepted_modes
    return mode_prop




class Job(ConfigInterface):
    def __init__(self, config=None, name=ANONYMOUS_JOB):
        """
        :type name: str
        :type config: dict
        """
        if config is None:
            config = {}

        self.name = name
        self._job_config = config

    def __add__(self, other):
        """
        When two jobs are added, we merge their config options, and in case there is a conflict, we retain the
        one from the right operand.

        :param other: The other Job we'd like to add
        :type other: Job
        :returns: A merged Job (anonymous)
        :rtype: Job
        """
        assert hasattr(other, "_job_config"), "This does not look like a job!"

        config = {}
        config.update(self._job_config)
        config.update(other._job_config)

        return Job(config)

    @property
    def mode(self):
        for k in ["rw", "readwrite"]:
            out = self._job_config.get(k)
            if out is not None:
                return out
        return DEFAULT_MODE

    is_read = property(make_mode_prop(READ_MODES))
    is_write = property(make_mode_prop(WRITE_MODES))

    @property
    def block_size(self):
        for param in ["bs", "blocksize"]:
            out = self._job_config.get(param, None)
            if out is not None:
                return out
        return DEFAULT_BLOCK_SIZE

    @property
    def io_depth(self):
        return self._job_config.get("iodepth", DEFAULT_IO_DEPTH)

    def to_ini(self):
        """
        Render as an ini config file.

        :returns: A string containing the ini config
        :rtype: str
        """

        stream = six.StringIO()

        cnf = configparser.ConfigParser(allow_no_value=True)
        cnf.add_section(self.name)
        for k, v in self._job_config.items():
            cnf.set(self.name, k, to_option(v))

        if six.PY3:
            cnf.write(stream, space_around_delimiters=False)
            stream.seek(0)
            return stream.read()
        else:
            cnf.write(stream)
            stream.seek(0)
            return stream.read().replace(" = ", "=")
