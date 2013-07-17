#!/usr/bin/env python3
#coding:utf-8
import os
import sys
import configparser
import tempfile
import subprocess
import itertools


GLOBAL_CONFIG = {
    #"clocksource": "cpu",
    "ioscheduler": "deadline",
    "ramp_time": 15,
    "randrepeat": 0,
    "ioengine": "libaio",
    "direct": 1,
}

def get_format(section):
    out = []
    for sub_section, elements in section:
        for element in elements:
            out.append("-".join([sub_section, element]))
    return out


# Defining the parser
_FORMAT_IO = ["kb", "bandwidth-kbps", "runtime-ms",]
_FORMAT_LATENCY = ["min", "max", "avg", "stddev"]
_FORMAT_BANDWIDTH = ["min", "max", "aggregate", "mean", "deviation"]
_FORMAT_CPU = ["user", "system", "context-switches", "major-faults", "minor-faults"]
_FORMAT_IO_DEPTH = ["<=1", "2", "4", "8", "16", "32", ">=64"]
_FORMAT_LATENCY_DISTRIBUTION_MICROSECONDS = ["<=2", "4", "10", "20", "50", "100", "250", "500", "750", "1000"]
_FORMAT_LATENCY_DISTRIBUTION_MILLISECONDS = _FORMAT_LATENCY_DISTRIBUTION_MICROSECONDS + ["2000", ">=2000"]
_ERROR_INFO = ["number-errors", "first-error-code"]

_FORMAT_STATUS = [
    ("io", _FORMAT_IO),
    ("latency", get_format([
        ("submission-usec", _FORMAT_LATENCY),
        ("completion-usec", _FORMAT_LATENCY),
        ("total-usec", _FORMAT_LATENCY),
        ])
    ),
    ("bandwidth", _FORMAT_BANDWIDTH),
]

FORMAT = get_format([
    ("general", ["version", "jobname", "groupid", "error"]),
    ("read", get_format(_FORMAT_STATUS)),
    ("write", get_format(_FORMAT_STATUS)),
    ("cpu", _FORMAT_CPU),
    ("io", get_format([
        ("depth", _FORMAT_IO_DEPTH),
        ("latency-microseconds", _FORMAT_LATENCY_DISTRIBUTION_MICROSECONDS),
        ("latency-milliseconds", _FORMAT_LATENCY_DISTRIBUTION_MILLISECONDS),
        ])
    ),
    ("additional-info", _ERROR_INFO)
])





class FioTest(object):
    def __init__(self, device, mode, file_size, block_size, io_depth, runtime):
        """
        :param device: The device to test against
        :param mode: The mode to test
        :param file_size: The file size to test with (in gigabytes)
        :param block_size: The blocksize to test with (in kilobytes)
        :param io_depth: The IO Depth to use
        :param runtime: The runtime for the test (seconds)
        """
        self.device = device
        self.mode = mode
        self.file_size = file_size
        self.block_size = block_size
        self.io_depth = io_depth
        self.runtime = runtime

    def _get_test_section(self):
        return {
            "filename": self.device,
            "rw": self.mode,
            "size": str(self.file_size) + "G",
            "bs": str(self.block_size) + "k",
            "iodepth": self.io_depth,
            "runtime": self.runtime,
            "stonewall": None,
        }

    def to_option(self, value):
        return str(value) if value is not None else None

    def generate_config(self, temp_dir):
        """
        Generate the FIO config
        """
        cnf = configparser.ConfigParser(allow_no_value=True)
        cnf.add_section("global")
        cnf.add_section("test")
        for k, v in GLOBAL_CONFIG.items():
            cnf.set("global", k, self.to_option(v))
        for k, v in self._get_test_section().items():
            cnf.set("test", k, self.to_option(v))

        config_path = os.path.join(temp_dir, "fio.conf")
        with open(config_path, "w") as f:
            cnf.write(f, space_around_delimiters=False)

        return config_path

    def execute_fio(self, config_file):
        """
        Execute the FIO run
        """
        args = ["sudo", "fio", "--minimal", "--timeout={0}".format(self.runtime + 20), config_file]
        return subprocess.check_output(args)  #TODO: We lose debug output here

    def run_test(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = self.generate_config(temp_dir)
            try:
                output = self.execute_fio(config_path)
            except subprocess.CalledProcessError as e:
                print("Error occured: {0}".format(e.returncode))
                print("Output: {0}".format(e.output))
                sys.exit(1)
            else:
                self.report(output.decode('utf-8'))

    def report(self, output):
        print("Finished")
        output_dict = dict(zip(FORMAT, output.split(";")))
        for k, v in output_dict.items():
            print("{0}:  {1}".format(k, v))


if __name__ == "__main__":
    modes = ["randread", "randwrite"]
    depths = [1, 4]
    block_sizes = [16, 64,128]
    for mode, depth, block_size in itertools.product(modes, depths, block_sizes):
        test = FioTest("/dev/xvdg", mode=mode, file_size=10, block_size=block_size, io_depth=depth, runtime=20)
        test.run_test()