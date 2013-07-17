#coding:utf-8
import io
import sys
import os
import configparser
import subprocess
import tempfile

from fio.exceptions import FIOInvalidVersion, FIOCallException
from fio.output import FORMAT


class FIOTest(object):
    _test_name = "fio-test"

    def __init__(self, config, fio_bin="fio"):
        """
        :param config: The configuration to use for this test (in FIO k,v format. Use None for no value)
        :param fio_bin: Where to find the fio binary
        """
        self.config = config
        self.fio_bin = fio_bin

    def to_option(self, value):
        return str(value) if value is not None else None

    def generate_config(self, temp_dir):
        """
        Generate the FIO config
        """
        cnf = configparser.ConfigParser(allow_no_value=True)
        cnf.add_section(self._test_name)
        for k, v in self.config.items():
            cnf.set(self._test_name, k, self.to_option(v))

        config_path = os.path.join(temp_dir, "fio.conf")
        with open(config_path, "w") as f:
            cnf.write(f, space_around_delimiters=False)

        return config_path

    def check_version(self):
        """
        Check that the version on FIO that is available is recent enough.
        """
        args = ["fio", "-v"]
        output = subprocess.check_output(args).decode('utf-8')
        _, version = output.split("-")
        major, minor, patch = map(int, version.split('.'))
        if major < 2:
            raise FIOInvalidVersion()

    def execute_fio(self, config_file):
        """
        Execute the FIO run
        """
        args = ["fio", "--minimal", "--warnings-fatal",config_file]

        stream_in, stream_out = io.BytesIO(), io.BytesIO()

        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = map(lambda s: s.decode("utf-8"), proc.communicate())

        ret_code = proc.returncode

        if ret_code != 0:
            raise FIOCallException(ret_code, stdout, stderr)

        return stdout

    def report(self, output):
        print("Finished")
        print(output)
        output_dict = dict(zip(FORMAT, output.split(";")))

        #if output_dict["general-version"] != "2":
        #    raise Exception("Invalid output format!")
        #if output_dict["general-error"] != "0":
        #    raise Exception("An error occurred!")

        for k, v in output_dict.items():
            print("{0}:  {1}".format(k, v))

    def run_test(self):
        self.check_version()
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = self.generate_config(temp_dir)
            output = self.execute_fio(config_path)
            self.report(output)
