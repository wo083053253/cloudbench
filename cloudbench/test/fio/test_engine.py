#coding:utf-8
import unittest
from cloudbench.fio.exceptions import FIOCallError
from cloudbench.fio.config.job import Job

from cloudbench.fio.engine import FIOEngine


class EngineArgsTestCase(unittest.TestCase):
    def test_version_args(self):
        engine = FIOEngine(Job())
        self.assertEqual(["fio", "-v"], engine._get_check_version_args())

        engine = FIOEngine(Job({"a": "b"}))
        self.assertEqual(["fio", "-v"], engine._get_check_version_args())

        engine = FIOEngine(Job(), "/usr/local/bin/fio")
        self.assertEqual(["/usr/local/bin/fio", "-v"], engine._get_check_version_args())

    def test_invocation_args(self):
        cnf_path = "/does/not/exist"
        engine = FIOEngine(Job())
        self.assertEqual(["fio", "--minimal", "--warnings-fatal", cnf_path], engine._get_execute_fio_args(cnf_path))

        engine = FIOEngine(Job(), "/usr/local/bin/fio")
        self.assertEqual(["/usr/local/bin/fio", "--minimal", "--warnings-fatal", cnf_path], engine._get_execute_fio_args(cnf_path))



class EngineInvocationTestCase(unittest.TestCase):
    def test_check_version(self):
        class TestEngine(FIOEngine):
            def _get_check_version_args(self):
                return ["echo", "fio-2.0.15"]

        engine = TestEngine(Job())
        engine.check_version()
        #TODO: Test with older version

    def test_execute(self):
        class TestEngine(FIOEngine):
            def _get_execute_fio_args(self, config_file):
                return ["echo", "Hello world"]

        engine = TestEngine(Job())

        output = engine.execute_fio("/does/not/exist")
        self.assertEqual(output, "Hello world")

    def test_fail_execution(self):
        class TestEngine(FIOEngine):
            def _get_execute_fio_args(self, config_file):
                return ["false"]

        engine = TestEngine(Job())
        self.assertRaises(FIOCallError, engine.execute_fio, "/does/not/exist")
