#coding:utf-8
class InvalidBlockSize(Exception):
    pass


BS_UNITS = {
    "k": 1,  # This is our base unit
    "m": 1024,
    "g": 1024**2,
    "t": 1024**3,
    "p": 1024**4,
    }


DISCARD_UNIT = "b"


def block_size_in_kb(bs):
    """
    :param bs: A fio-compliant block size (We don't support base 10 at the moment)
    :return: The same block size, in kilobytes
    """

    exc = InvalidBlockSize(bs)  # In case we need to raise this later

    bs, unit = map(lambda s: s.lower(), [bs[:-1], bs[-1]])

    if unit == DISCARD_UNIT:
        return block_size_in_kb(bs)

    try:
        bs = int(bs)
        factor = BS_UNITS[unit]
    except (ValueError, KeyError):
        raise exc

    return bs * factor

