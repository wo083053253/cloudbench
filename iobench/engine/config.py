#coding:utf-8
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
