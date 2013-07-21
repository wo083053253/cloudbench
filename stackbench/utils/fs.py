#coding:utf-8
import os
import stat
import logging

logger = logging.getLogger(__name__)


def check_filename(filename):
    """
    Perform a routine check of the filename / device.
    We:
      + Ensure that if it's in /dev, it exists, and it's a block device

    :type filename: str
    """
    try:
       mode = os.stat(filename).st_mode
    except OSError:
        logging.debug("File does not exist")
        is_block = False
    else:
        is_block = stat.S_ISBLK(mode)
        logging.debug("%s is a block device: %s", filename, is_block)

    if filename.startswith("/dev"):
        assert is_block, "%s is not a block device. Is that what you want to be doing?" % filename

