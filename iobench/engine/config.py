#coding:utf-8
import configparser
import io

from iobench.engine.exceptions import FIOInvalidConfigValue


MULTIPLIERS = ["k", "M", "G", "T", "P"]
UNITS = []
UNITS.extend(MULTIPLIERS)
UNITS.extend([unit + "b" for unit in MULTIPLIERS])
UNITS.extend([unit + "iB" for unit in MULTIPLIERS])


def coerce_size(size):
    for unit in UNITS:
        if size.endswith(unit):
            try:
                _ = int(size[-len(unit)])
            except ValueError:
                pass
            else:
                return size
    raise FIOInvalidConfigValue()


def to_option(value):
    return str(value) if value is not None else None


class FIOConfig(object):
    def __init__(self):
        self._state = []

    def add_job(self, name, conf):
        self._state.append((name, conf))

    def add_global(self, conf):
        self.add_job("global", conf)

    def to_ini(self):
        # Generate the ini config
        # We have to use this stream because ConfigParser would not support duplicate sections
        stream = io.StringIO()

        for name, conf in self._state:
            cnf = configparser.ConfigParser(allow_no_value=True)
            cnf.add_section(name)
            for k, v in conf.items():
                cnf.set(name, k, to_option(v))
            cnf.write(stream, False)

        stream.seek(0)
        return stream.read()

    def jobs(self):
        return [conf for name, conf in self._state if name != "global"]