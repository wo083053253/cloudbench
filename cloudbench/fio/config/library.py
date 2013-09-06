#coding:utf-8
from cloudbench.fio.config.job import Job

BASE_LINUX_JOB = Job({
    "clocksource": "cpu",
    "randrepeat": "0",
    "group_reporting": None,
    "direct": "1",
    "ioengine": "libaio",
})


BASE_FILL_JOB = Job({
    "scramble_buffers": "1",
    "iodepth": "4",
    "rw": "write",
    "bs": "2M",
    "refill_buffers": None,
})


BENCH_JOB = Job({
    "ioscheduler": "deadline",
    "cpumask": "1",  #TODO ????
    "time_based": None,
    #"rate_iops": "2000",
})
