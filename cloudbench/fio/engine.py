#coding:utf-8
import os
import shutil
import subprocess
import tempfile
import logging

from cloudbench.fio.exceptions import FIOInvalidVersion, FIOCallError, FIOError
from cloudbench.fio.output import FORMAT


logger = logging.getLogger()


class FIOEngine(object):
    _test_name = "fio-test"

    def __init__(self, config, fio_bin="fio"):
        """
        :param config: A FIO Config object to use for the tests
        :type config: cloudbench.fio.config.ConfigInterface
        :param fio_bin: Where to find the fio binary
        :type fio_bin: str
        """
        self.config = config
        self.fio_bin = fio_bin

    def generate_config(self, temp_dir):
        """
        Generate the FIO config
        """
        config_path = os.path.join(temp_dir, "fio.ini")

        with open(config_path, "w") as f:
            f.write(self.config.to_ini())

        return config_path

    def _get_check_version_args(self):
        return [self.fio_bin, "-v"]

    def check_version(self):
        """
        Check that the version of FIO that is available is recent enough.
        """
        args = self._get_check_version_args()
        output = subprocess.check_output(args).decode('utf-8')  #TODO: Versions?
        _, version = output.split("-")
        major, minor, patch = map(int, version.split('.'))
        if major < 2:
            raise FIOInvalidVersion()

    def _get_execute_fio_args(self, config_file):
        return [self.fio_bin, "--minimal", "--warnings-fatal", config_file]

    def execute_fio(self, config_file):
        """
        Execute the FIO run
        """
        args = self._get_execute_fio_args(config_file)

        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = map(lambda s: s.decode("utf-8").strip('\n'), proc.communicate())
        ret_code = proc.returncode

        if ret_code != 0:
            raise FIOCallError(ret_code, stdout, stderr)

        return stdout

    def report(self, fio_output):
        """
        :param fio_output:
        :type fio_output: str
        :returns: A list of reports (dicts), one per reporting group
        :rtype: list of dict
        :raises: FIOError
        """
        report = []

        for reporting_group in fio_output.split("\n"):
            if reporting_group.startswith("fio:"):
                logger.warning("Received fio warning: %s", reporting_group)
                continue

            d = dict(zip(FORMAT, reporting_group.split(";")))

            if d["general-terse-version"] != "3":
                raise FIOError("Invalid output format!")
            if d["general-error"] != "0":
                raise FIOError("An error occurred!")

            report.append(d)

        return report

    def run_test(self):
        self.check_version()
        temp_dir = tempfile.mkdtemp()  # No context manager on older pythons!

        config_path = self.generate_config(temp_dir)
        output = self.execute_fio(config_path)

        shutil.rmtree(temp_dir)
        return self.report(output)
