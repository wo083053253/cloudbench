#coding:utf-8
import unittest

from cloudbench.fio.config.job import Job
from cloudbench.fio.engine import FIOEngine
from cloudbench.fio.report.single import SingleJobReport

REPORT = "3;cloudbench-2.0.15;cloudbench-test;0;0;506416;25319;1582.22;20001;0;0;0.000000;0.000000;3;26586;420.649806;" \
         "529.499685;1.000000%=6;5.000000%=15;10.000000%=159;20.000000%=177;30.000000%=306;40.000000%=326;" \
         "50.000000%=334;60.000000%=342;70.000000%=358;80.000000%=386;90.000000%=580;95.000000%=1416;99.000000%=2512;" \
         "99.500000%=2864;99.900000%=4448;99.950000%=6880;99.990000%=14272;0%=0;0%=0;0%=0;3;26586;420.892105;" \
         "529.513887;19040;32736;100.000000%;25415.538462;2541.598635;501760;25086;1567;20001;0;0;0.000000;0.000000;" \
         "119;18453;205.181728;327.126181;1.000000%=141;5.000000%=145;10.000000%=147;20.000000%=151;30.000000%=153;" \
         "40.000000%=157;50.000000%=161;60.000000%=167;70.000000%=175;80.000000%=195;90.000000%=219;95.000000%=274;" \
         "99.000000%=1256;99.500000%=1736;99.900000%=4016;99.950000%=6304;99.990000%=14144;0%=0;0%=0;0%=0;120;" \
         "18454;206.068463;327.190851;1;33213;97.760803%;24524.275000;4709.625011;2.740000%;16.595000%;113242;5;0;" \
         "173.0%;0.0%;0.0%;0.0%;0.0%;0.0%;0.0%;0.00%;0.01%;2.34%;0.18%;0.01%;0.01%;57.97%;32.27%;2.13%;1.02%;2.53%;" \
         "1.41%;0.10%;0.02%;0.01%;0.00%;0.00%;0.00%;0.00%;0.00%;0.00%;0.00%"


class TestSingleJobReport(unittest.TestCase):
    def setUp(self):
        dummy_job = Job()
        engine = FIOEngine(dummy_job)
        self.output = engine.report(REPORT)

    def test_aggregation(self):
        """
        Test that we only report values relevant for the current test
        """
        job = Job({"rw":"read"})
        report = SingleJobReport(job, self.output[0])
        self.assertEqual(1582, report.avg_iops)

        job = Job({"rw":"write"})
        report = SingleJobReport(job, self.output[0])
        self.assertEqual(1567, report.avg_iops)

        job = Job({"rw":"rw"})
        report = SingleJobReport(job, self.output[0])
        self.assertEqual(1567 + 1582, report.avg_iops)
