#coding:utf-8
from cloudbench.fio.config import ConfigInterface


class FIOConfig(ConfigInterface):
    def __init__(self):
        self._jobs = []

    def add_job(self, job):
        """
        Add a job at the end of this configuration

        :param job: The job to add
        :type job: cloudbench.fio.config.job.Job
        """
        self._jobs.append(job)

    def to_ini(self):
        """
        Render this configuration as an ini file.

        :returns: The configuration
        :rtype: str
        """
        return "\n".join(job.to_ini() for job in self._jobs)