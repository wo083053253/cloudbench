#coding:utf-8
import unittest
import decimal

from cloudbench.fio.config.job import Job
from cloudbench.fio.engine import FIOEngine
from cloudbench.fio.report.single import SingleJobReport


# We can't get FIO to report both minimal (terse) and regular output, so we ran two tests that should produce
# similar results
# 16k-1-read: (g=0): rw=rw, bs=16K-16K/16K-16K/16K-16K, ioengine=sync, iodepth=1
# fio-2.0.15
# Starting 1 thread
# Jobs: 1 (f=1), CR=4000/0 IOPS: [M] [100.0% done] [8352K/7648K/0K /s] [522 /478 /0  iops] [eta 00m:00s]
# 16k-1-read: (groupid=0, jobs=1): err= 0: pid=18193: Mon Sep  9 11:42:55 2013
#   read : io=77552KB, bw=7753.7KB/s, iops=484 , runt= 10002msec
#     clat (usec): min=560 , max=3291 , avg=711.07, stdev=193.33
#      lat (usec): min=561 , max=3291 , avg=711.35, stdev=193.33
#     clat percentiles (usec):
#      |  1.00th=[  580],  5.00th=[  588], 10.00th=[  604], 20.00th=[  620],
#      | 30.00th=[  636], 40.00th=[  660], 50.00th=[  676], 60.00th=[  684],
#      | 70.00th=[  700], 80.00th=[  732], 90.00th=[  804], 95.00th=[  956],
#      | 99.00th=[ 1592], 99.50th=[ 1944], 99.90th=[ 2672], 99.95th=[ 2800],
#      | 99.99th=[ 3280]
#     bw (KB/s)  : min= 6048, max= 8800, per=99.91%, avg=7745.68, stdev=695.83
#   write: io=76848KB, bw=7683.3KB/s, iops=480 , runt= 10002msec
#     clat (usec): min=1052 , max=6044 , avg=1356.21, stdev=320.30
#      lat (usec): min=1053 , max=6044 , avg=1358.79, stdev=320.28
#     clat percentiles (usec):
#      |  1.00th=[ 1128],  5.00th=[ 1176], 10.00th=[ 1192], 20.00th=[ 1208],
#      | 30.00th=[ 1224], 40.00th=[ 1240], 50.00th=[ 1256], 60.00th=[ 1272],
#      | 70.00th=[ 1320], 80.00th=[ 1400], 90.00th=[ 1592], 95.00th=[ 1928],
#      | 99.00th=[ 2928], 99.50th=[ 3216], 99.90th=[ 3952], 99.95th=[ 4256],
#      | 99.99th=[ 6048]
#     bw (KB/s)  : min=   15, max= 8576, per=95.12%, avg=7307.95, stdev=1831.72
#     lat (usec) : 750=42.02%, 1000=6.01%
#     lat (msec) : 2=49.50%, 4=2.44%, 10=0.03%
#   cpu          : usr=4.80%, sys=0.00%, ctx=10619, majf=0, minf=4
#   IO depths    : 1=110.0%, 2=0.0%, 4=0.0%, 8=0.0%, 16=0.0%, 32=0.0%, >=64=0.0%
#      submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
#      complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
#      issued    : total=r=4847/w=4803/d=0, short=r=0/w=0/d=0
#
# Run status group 0 (all jobs):
#    READ: io=77552KB, aggrb=7753KB/s, minb=7753KB/s, maxb=7753KB/s, mint=10002msec, maxt=10002msec
#   WRITE: io=76848KB, aggrb=7683KB/s, minb=7683KB/s, maxb=7683KB/s, mint=10002msec, maxt=10002msec
#
# Disk stats (read/write):
#   xvda1: ios=5272/5248, merge=0/10, ticks=3704/7016, in_queue=10720, util=97.54%


REPORT = "3;fio-2.0.15;16k-1-read;0;0;77968;7796;487;10001;0;0;0.000000;0.000000;555;2648;720.394213;198.444542;" \
         "1.000000%=564;5.000000%=580;10.000000%=596;20.000000%=612;30.000000%=636;40.000000%=660;50.000000%=676;" \
         "60.000000%=692;70.000000%=708;80.000000%=748;90.000000%=868;95.000000%=1048;99.000000%=1656;99.500000%=1976;" \
         "99.900000%=2480;99.950000%=2640;99.990000%=2640;0%=0;0%=0;0%=0;555;2648;720.603324;198.447383;15;8896;" \
         "94.723576%;7384.650000;1846.619366;76640;7663;478;10001;0;0;0.000000;0.000000;1046;5286;1345.434656;" \
         "299.810440;1.000000%=1144;5.000000%=1160;10.000000%=1176;20.000000%=1192;30.000000%=1208;40.000000%=1224;" \
         "50.000000%=1240;60.000000%=1272;70.000000%=1320;80.000000%=1416;90.000000%=1592;95.000000%=1928;" \
         "99.000000%=2800;99.500000%=2992;99.900000%=3280;99.950000%=3792;99.990000%=5280;0%=0;0%=0;0%=0;1050;5290;" \
         "1349.806263;299.806389;6496;8288;99.825546%;7649.631579;552.433728;4.040000%;0.000000%;10592;0;4;109.6%;0.0%;" \
         "0.0%;0.0%;0.0%;0.0%;0.0%;0.00%;0.00%;0.00%;0.00%;0.00%;0.00%;0.00%;0.00%;40.23%;7.15%;50.28%;2.32%;0.02%;" \
         "0.00%;0.00%;0.00%;0.00%;0.00%;0.00%;0.00%;0.00%;0.00%;xvda1;5285;5188;0;2;3752;7032;10788;98.16%"


class TestSingleJobReport(unittest.TestCase):
    def setUp(self):
        dummy_job = Job()
        engine = FIOEngine(dummy_job)
        self.output = engine.report(REPORT)

    def test_iops(self):
        job = Job({"rw":"read"})
        report = SingleJobReport(job, self.output[0])
        self.assertEqual(decimal.Decimal("487"), report.avg_iops)

        job = Job({"rw":"write"})
        report = SingleJobReport(job, self.output[0])
        self.assertEqual(decimal.Decimal("478"), report.avg_iops)

        job = Job({"rw":"rw"})
        report = SingleJobReport(job, self.output[0])
        self.assertEqual(decimal.Decimal("965"), report.avg_iops)

    def test_avg_bw(self):
        job = Job({"rw": "read"})
        report = SingleJobReport(job, self.output[0])
        self.assertEqual(decimal.Decimal("7384.65000"), report.avg_bw)

        job = Job({"rw": "write"})
        report = SingleJobReport(job, self.output[0])
        self.assertEqual(decimal.Decimal("7649.63158"), report.avg_bw)

        job = Job({"rw": "rw"})
        report = SingleJobReport(job, self.output[0])
        self.assertEqual(decimal.Decimal("15034.28158"), report.avg_bw)

    def test_stddev_bw(self):
        job = Job({"rw": "read"})
        report = SingleJobReport(job, self.output[0])
        self.assertEqual(decimal.Decimal("1846.61937"), report.stddev_bw)

        job = Job({"rw": "write"})
        report = SingleJobReport(job, self.output[0])
        self.assertEqual(decimal.Decimal("552.43373"), report.stddev_bw)

        job = Job({"rw": "rw"})
        report = SingleJobReport(job, self.output[0])
        self.assertEqual(decimal.Decimal("2399.05309"), report.stddev_bw)


    def test_avg_latency(self):
        job = Job({"rw": "read"})
        report = SingleJobReport(job, self.output[0])
        self.assertEqual(decimal.Decimal("720.60332"), report.avg_lat)

        job = Job({"rw": "write"})
        report = SingleJobReport(job, self.output[0])
        self.assertEqual(decimal.Decimal("1349.80626"), report.avg_lat)

        job = Job({"rw": "rw"})
        report = SingleJobReport(job, self.output[0])
        self.assertEqual(decimal.Decimal("1035.20479"), report.avg_lat)

    def test_stddev_latency(self):
        job = Job({"rw": "read"})
        report = SingleJobReport(job, self.output[0])
        self.assertEqual(decimal.Decimal("198.44738"), report.stddev_lat)

        job = Job({"rw": "write"})
        report = SingleJobReport(job, self.output[0])
        self.assertEqual(decimal.Decimal("299.80639"), report.stddev_lat)

        job = Job({"rw": "rw"})
        report = SingleJobReport(job, self.output[0])
        self.assertEqual(decimal.Decimal("249.12689"), report.stddev_lat)
