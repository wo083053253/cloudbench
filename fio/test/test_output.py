#coding:utf-8
import unittest

from fio.output import FORMAT


class OutputParserTestCase(unittest.TestCase):
    def test_format(self):
        out = "2;test;0;0;126756;6484;20018;10;24205;12.218181;134.847987;370;52087;617.482802;1304.541812;383;52098;629.629221;1304.599063;0;7344;97.693067%;6185.925000;1157.422144;0;0;0;0;0;0.000000;0.000000;0;0;0.000000;0.000000;0;0;0.000000;0.000000;0;0;0.000000%;0.000000;0.000000;2.078234%;8.372883%;54530;0;20;171.4%;0.0%;0.0%;0.0%;0.0%;0.0%;0.0%;0.00%;0.00%;0.00%;0.00%;0.00%;0.00%;0.00%;68.33%;22.24%;5.42%;3.19%;0.42%;0.05%;0.07%;0.27%;0.01%;0.00%;0.00%;0.00%;0.00%;0.00%;0.00%"
        dict_output = dict(zip(FORMAT, out.split(";")))
        self.assertNotIn("additional-info-number-errors", dict_output.keys())  # We should not have this here!
        self.assertEqual(dict_output["io-latency-microseconds-750"], "22.24%")
        self.assertEqual(dict_output["read-bandwidth-aggregate"], "97.693067%")
        self.assertEqual(dict_output["read-latency-submission-usec-min"], "10")