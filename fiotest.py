#!/usr/bin/env python3
#coding:utf-8
from fio.engine import FIOTest


if __name__ == "__main__":
    config = {
        # General config
        #"ioscheduler": "deadline",  # Linux Only
        "ramp_time": 15,
        "randrepeat": 0,
        #"ioengine": "libaio", # Linux Only
        "direct": 1,

        # Mac OS only
        "thread": None,

        # Test specific
        "filename": "/tmp/afile",
        "rw": "randread",
        "size": "1G",
        "bs": "16k",
        "iodepth": 4,
        "runtime": 20,
        "stonewall": None
    }

    test = FIOTest(config)
    test.run_test()


    #modes = ["randread", "randwrite"]
    #depths = [1, 4]
    #block_sizes = [16, 64,128]  #--> TODO: "16k"
    #for mode, depth, block_size in itertools.product(modes, depths, block_sizes):
    #    test = FioTest("/dev/xvdg", mode=mode, file_size=10, block_size=block_size, io_depth=depth, runtime=20)
    #    test.run_test()