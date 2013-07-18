#coding:utf-8
import os
import configparser
import subprocess
import tempfile

from iobench.engine.exceptions import FIOInvalidVersion, FIOCallException
from iobench.engine.output import FORMAT


class FIOEngine(object):
    _test_name = "iobench-test"

    def __init__(self, config, fio_bin="iobench"):
        """
        :param config: The configuration to use for this test (in FIO k,v format. Use None for no value)
        :param fio_bin: Where to find the iobench binary
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

        config_path = os.path.join(temp_dir, "iobench.conf")
        with open(config_path, "w") as f:
            cnf.write(f, space_around_delimiters=False)

        return config_path

    def check_version(self):
        """
        Check that the version on FIO that is available is recent enough.
        """
        args = ["iobench", "-v"]
        output = subprocess.check_output(args).decode('utf-8')
        _, version = output.split("-")
        major, minor, patch = map(int, version.split('.'))
        if major < 2:
            raise FIOInvalidVersion()

    def execute_fio(self, config_file):
        """
        Execute the FIO run
        """
        args = ["iobench", "--minimal", "--warnings-fatal",config_file]

        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = map(lambda s: s.decode("utf-8").strip('\n'), proc.communicate())
        ret_code = proc.returncode

        if ret_code != 0:
            raise FIOCallException(ret_code, stdout, stderr)

        return stdout

    def report(self, output):
        output_dict = dict(zip(FORMAT, output.split(";")))

        if output_dict["general-terse-version"] != "3":
            raise Exception("Invalid output format!")
        if output_dict["general-error"] != "0":
            raise Exception("An error occurred!")

        return output_dict

    def run_test(self):
        self.check_version()
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = self.generate_config(temp_dir)
            output = self.execute_fio(config_path)

        return self.report(output)
