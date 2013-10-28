#coding:utf-8

def get_format(section):
    out = []
    for sub_section, elements in section:
        for element in elements:
            out.append("-".join([sub_section, element]))
    return out


_FORMAT_IO = ["total-kb", "bandwidth-kbps", "iops", "runtime-ms"]
_FORMAT_LATENCY = ["min", "max", "avg", "stddev"]
_FORMAT_PERCENTILE = ["pct-{0}".format(i) for i in range(20)]
_FORMAT_BANDWIDTH = ["min", "max", "aggregate", "avg", "stddev"]
_FORMAT_CPU = ["user", "system", "context-switches", "major-page-faults", "minor-page-faults"]
_FORMAT_IO_DEPTH = ["<=1", "2", "4", "8", "16", "32", ">=64"]
_FORMAT_LATENCY_DISTRIBUTION_MICROSECONDS = ["<=2", "4", "10", "20", "50", "100", "250", "500", "750", "1000"]
_FORMAT_LATENCY_DISTRIBUTION_MILLISECONDS = _FORMAT_LATENCY_DISTRIBUTION_MICROSECONDS + ["2000", ">=2000"]
_ERROR_INFO = ["number-errors", "first-error-code"]


_FORMAT_STATUS = [
    ("io", _FORMAT_IO),
    ("latency-usec", get_format([
        ("submission", _FORMAT_LATENCY),
        ("completion", _FORMAT_LATENCY),
        ("completion-percentiles", _FORMAT_PERCENTILE),
        ("total", _FORMAT_LATENCY),
        ])
    ),
    ("bandwidth", _FORMAT_BANDWIDTH),
]

FORMAT = get_format([
    ("general", ["terse-version", "fio-version", "jobname", "groupid", "error"]),
    ("read", get_format(_FORMAT_STATUS)),
    ("write", get_format(_FORMAT_STATUS)),
    ("cpu", _FORMAT_CPU),
    ("io-distribution", get_format([
        ("depth", _FORMAT_IO_DEPTH),
        ("latency-microseconds", _FORMAT_LATENCY_DISTRIBUTION_MICROSECONDS),
        ("latency-milliseconds", _FORMAT_LATENCY_DISTRIBUTION_MILLISECONDS),
        ])
    ),
    #("additional-info", _ERROR_INFO) # We don't continue on error
])
