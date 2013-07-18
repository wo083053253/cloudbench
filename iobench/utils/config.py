#coding:utf-8

def get_mode(job_conf):
    return job_conf.get("rw", job_conf.get("readwrite"))

def is_read(job_conf):
    return get_mode(job_conf) in ["read", "randread", "rw", "readwrite", "randrw"]


def is_write(job_conf):
    return get_mode(job_conf) in ["write", "randwrite", "rw", "readwrite", "randrw"]

