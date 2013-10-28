#coding:utf-8
import decimal

from cloudbench.fio.report import REPORT_DECIMAL_Q


class SingleJobReport(object):
    """
    Process the output of a single job.
    """
    def __init__(self, job, report):
        """
        :param job: The Job this report was generated from
        :type job: cloudbench.fio.config.job.Job
        :param report: A report generated by the engine
        :type report: dict
        """
        self.job = job
        self.report = report

    # IOPS are "shared" on a mixed workload
    # So we use the sum
    @property
    def avg_iops(self):
        return self._property_sum("io-iops")

    # Latency isn't "shared" on a mixed workload
    # So we use the average
    @property
    def avg_lat(self):
        return self._property_average("latency-usec-total-avg")

    @property
    def stddev_lat(self):
        return self._property_average("latency-usec-total-stddev")

    # Bandwidth is "shared" on a mixed workload
    # So we use the sum
    @property
    def avg_bw(self):
        return self._property_sum("bandwidth-avg")

    @property
    def stddev_bw(self):
        return self._property_sum("bandwidth-stddev")

    def _io_modes(self):
        return [mode for mode, is_mode in [("read", self.job.is_read), ("write", self.job.is_write)] if is_mode]

    def _raw_property_sum(self, prop):
        value = decimal.Decimal()
        for io_mode in self._io_modes():
            value += decimal.Decimal(self.report["{0}-{1}".format(io_mode, prop)])
        return value

    def _property_sum(self, prop):
        value = self._raw_property_sum(prop)
        return value.quantize(REPORT_DECIMAL_Q)

    def _property_average(self, prop):
        io_modes = self._io_modes()
        if not io_modes:
            return 0
        value = self._raw_property_sum(prop) / decimal.Decimal(len(io_modes))
        return value.quantize(REPORT_DECIMAL_Q)
