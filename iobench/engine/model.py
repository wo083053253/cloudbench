#coding:utf-8
import os
import subprocess
import tempfile

from iobench.engine.exceptions import FIOInvalidVersion, FIOCallException
from iobench.engine.output import FORMAT


class FIOEngine(object):
    _test_name = "fio-test"

    def __init__(self, config, fio_bin="fio"):
        """
        :param config: A FIO Config object to use for the tests
        :type config: iobench.engine.config.FIOConfig
        :param fio_bin: Where to find the fio binary
        :type fio_bin: str
        """
        self.config = config
        self.fio_bin = fio_bin

    def to_option(self, value):
        return str(value) if value is not None else None

    def generate_config(self, temp_dir):
        """
        Generate the FIO config
        """
        config_path = os.path.join(temp_dir, "fio.ini")

        with open(config_path, "w") as f:
            f.write(self.config.to_ini())

        return config_path

    def check_version(self):
        """
        Check that the version of FIO that is available is recent enough.
        """
        args = [self.fio_bin, "-v"]
        output = subprocess.check_output(args).decode('utf-8')
        _, version = output.split("-")
        major, minor, patch = map(int, version.split('.'))
        if major < 2:
            raise FIOInvalidVersion()

    def execute_fio(self, config_file):
        """
        Execute the FIO run
        """
        args = [self.fio_bin, "--minimal", "--warnings-fatal",config_file]

        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = map(lambda s: s.decode("utf-8").strip('\n'), proc.communicate())
        ret_code = proc.returncode

        if ret_code != 0:
            raise FIOCallException(ret_code, stdout, stderr)

        return stdout

    def report(self, output):
        report = []

        for conf, output in zip(self.config.jobs(), output.split("\n")):
            output_dict = dict(zip(FORMAT, output.split(";")))

            if output_dict["general-terse-version"] != "3":
                raise Exception("Invalid output format!")
            if output_dict["general-error"] != "0":
                raise Exception("An error occurred!")

            report.append((conf, output_dict))

        return report

    def run_test(self):
        self.check_version()
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = self.generate_config(temp_dir)
            output = self.execute_fio(config_path)

        return self.report(output)
