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



def make_property(name, coerce_function=lambda x:x):
    """
    Create a property to use in configuration
    """
    assert not name.startswith('_')

    attr_name = "_" + name

    def getter(self):
        return getattr(self, attr_name)

    def setter(self, value):
        setattr(self, attr_name, coerce_function(value))

    return property(getter, setter)


class FIOConfig(object):
    """
    A model representing a FIO config. Meant to be extended with required options.
    """