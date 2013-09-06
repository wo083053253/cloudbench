#coding:utf-8
import sys
import argparse
import logging
import itertools

import lockfile.pidlockfile
from six.moves import configparser

from cloudbench.api.client import Client
from cloudbench.api.auth import APIKeyAuth
from cloudbench.cloud import Cloud
from cloudbench.fio.config.job import Job
from cloudbench.fio.config.library import BASE_LINUX_JOB, BASE_FILL_JOB
from cloudbench.fio.engine import FIOEngine
from cloudbench.fio.report.single import SingleJobReport
from cloudbench.utils.daemon import DaemonContext
from cloudbench.utils.fs import check_filename


logger = logging.getLogger()
logger.setLevel("DEBUG")


DEFAULT_CONFIG_FILE = "/etc/cloudbench.ini"
DEFAULT_FIO_PATH = "/usr/local/bin/fio"
DEFAULT_PID_FILE = "/var/run/cloudbench.pid"
DEFAULT_LOG_FILE = "/var/log/cloudbench.log"

DEFAULT_FILE_SIZE = "10G"
DEFAULT_RAMP_TIME = "15"
DEFAULT_DURATION = "600"



def setup_logging(log_file):
    """
    Configure logging for this run

    :returns: The list of streams to preserve when daemonizing
    :rtype: list of str
    """
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    # Silence libraries
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("boto").setLevel(logging.WARNING)

    return [file_handler.stream]


def may_bench(nobench, device):
    """
    Whether the given device may be benchmarked, provided a list of device prefixes not to benchmark
    Intended as a safeguard against accidentally benchmarking the root device

    :param nobench: List of device prefixes to not benchmark
    :param device: The candidate device
    :rtype: bool
    :returns: Whether this device may be benchmarked
    """
    for prefix in nobench:
        if device.startswith(prefix):
            return False
    return True


def identify_benchmark_volume(cloud, nobench):
    """
    Identify the volume we are going to benchmark

    :param cloud: Current Cloud environment
    :type cloud: cloudbench.cloud.base.BaseCloud
    :param nobench: List of device prefixes not to benchmark
    :type nobench: list of str

    :returns: The Volume to benchmark
    :rtype: cloudbench.cloud.base.BaseVolume
    """
    persistent_volumes = [volume for volume in cloud.attachments if volume.persistent]
    acceptable_volumes = [volume for volume in persistent_volumes if may_bench(nobench, volume.device)]

    if not acceptable_volumes:
        _devices = [vol.device for vol in persistent_volumes]
        raise Exception("No volume to benchmark. None of {0} is acceptable", ", ".join(_devices))

    if len(acceptable_volumes) > 1:
        _devices = [vol.device for vol in acceptable_volumes]
        raise Exception("Too many volumes: {0}".format(", ".join(_devices)))

    # Found the volume, move on!
    benchmark_volume = acceptable_volumes[0]
    check_filename(benchmark_volume.device)

    return benchmark_volume


def create_api_assets(cloud, api_client, benchmark_volume):
    provider = api_client.providers.get_or_create(name=cloud.provider)
    location = api_client.locations.get_or_create(name=cloud.location, provider=provider)
    instance_type = api_client.abstract_assets.get_or_create(name=cloud.instance_type)
    volume_type = api_client.abstract_assets.get_or_create(name=benchmark_volume.provider)
    instance = api_client.physical_assets.get_or_create(asset=instance_type, location=location)
    volume = api_client.physical_assets.get_or_create(asset=volume_type, location=location)
    return [instance, volume]


def warm_volume(base_job, fio_bin):
    fill_job = base_job + BASE_FILL_JOB
    engine = FIOEngine(fill_job, fio_bin)
    engine.run_test()


def report_benchmark(api_client, assets, configuration, job_report):
    for metric, value in [("IOPS", job_report.avg_iops), ("LAT", job_report.avg_lat), ("BW", job_report.avg_lat)]:

        api_client.measurements.create(
            configuration=configuration,
            assets=[a for a in assets],
            metric=metric,
            value=value,
        )

        logger.debug("Reported")
        logger.debug("Assets: %s", ", ".join([asset["asset"]["name"] for asset in assets]))
        logger.debug("Metric: %s", metric)
        logger.debug("Value: %s", value)


def run_benchmarks(api_client, assets, base_job, fio_bin, block_sizes, depths, modes):
    for i, (bs, depth, mode) in enumerate(itertools.product(block_sizes, depths, modes)):
        logger.info("Launching job. Block Size:%s, I/O Depth:%s, I/O Mode:%s", bs, depth, mode)

        job = base_job + Job({
            "bs": bs,
            "iodepth": depth,
            "rw": mode,
            "stonewall": None,
        })

        configuration = api_client.configurations.get_or_create( {
                "mode": job.mode,
                "block_size": job.block_size.rstrip("k"),  # The API excepts an integer here.
                "io_depth": job.io_depth
        })

        engine = FIOEngine(job, fio_bin)
        report = engine.run_test()
        assert len(report) == 1, "Invalid report: {0}".format(report)
        job_report = SingleJobReport(job, report[0])
        report_benchmark(api_client, assets, configuration, job_report)


def start_benchmark(cloud, api_client, benchmark_volume, fio_bin,  block_sizes, depths, modes, size, ramp, duration):
    # Create references in the API
    logging.debug("Creating API assets")
    assets = create_api_assets(cloud, api_client, benchmark_volume)

    # Prepare jobs
    base_job = BASE_LINUX_JOB + Job({
        "filename": benchmark_volume.device,
        "size": size,
        "ramp_time": ramp,
        "runtime": duration,
        })

    # Warm up the disk
    logging.debug("Running warm-up job")
    warm_volume(base_job, fio_bin)

    # Run benchmarks
    run_benchmarks(api_client, assets, base_job, fio_bin, block_sizes, depths, modes)


def _cnf_get_list(config, section, key):
    list_ = config.get(section, key).split(',')
    return [element.strip() for element in list_ if element.strip()]


def main():
    parser = argparse.ArgumentParser(description="Benchmark your Cloud performance")
    parser.add_argument("-c", "--config",
                        help="Path to the cloudbench configuration file (defaults to {0})".format(DEFAULT_CONFIG_FILE),
                        default=DEFAULT_CONFIG_FILE)

    args = parser.parse_args()

    config = configparser.ConfigParser({
        "fio":DEFAULT_FIO_PATH,
        "pidfile": DEFAULT_PID_FILE,
        "logfile":DEFAULT_LOG_FILE,
        "nobench": "",
        "size": DEFAULT_FILE_SIZE,
        "ramp": DEFAULT_RAMP_TIME,
        "duration": DEFAULT_DURATION
    })
    config.add_section("environment")
    config.add_section("general")
    config.read(args.config)

    fio_bin = config.get("environment", "fio")
    pid_file = config.get("environment", "pidfile")
    log_file = config.get("environment", "logfile")
    no_bench = _cnf_get_list(config, "environment", "nobench")

    files_preserve = setup_logging(log_file)

    block_sizes = _cnf_get_list(config, "benchmarks", "blocksizes")
    depths = _cnf_get_list(config, "benchmarks", "depths")
    modes = _cnf_get_list(config, "benchmarks", "modes")

    size = config.get("general", "size")
    ramp = config.get("general", "ramp")
    duration = config.get("general", "duration")

    reporting_endpoint = config.get("reporting", "endpoint")
    reporting_username = config.get("reporting", "username")
    reporting_key = config.get("reporting", "apikey")


    # Final setup options before we daemonize, to let the user catch misconfiguration errors
    cloud = Cloud()
    volume = identify_benchmark_volume(cloud, no_bench)

    api = Client(reporting_endpoint, APIKeyAuth(reporting_username, reporting_key))

    logging.info("Provider: %s", cloud.provider)
    logging.info("Location: %s", cloud.location)
    logging.info("Instance type: %s", cloud.instance_type)
    logging.info("Volume Type: %s, %s", volume.provider, "Persistent" if volume.persistent else "Ephemeral")

    logging.debug("Daemonizing")

    with DaemonContext(files_preserve=files_preserve, pidfile=lockfile.pidlockfile.PIDLockFile(pid_file)):
        try:
            start_benchmark(cloud, api, volume, fio_bin, block_sizes, depths, modes, size, ramp, duration)
        except Exception as e:
            logger.critical("An error occurred")
            response = getattr(e, "response", None)

            if response is not None:
                logger.critical("HTTP Error")
                logger.critical("Status: %s %s", response.status_code, response.reason)
                logger.critical("Response: %s", response.text)

            logger.exception("Fatal Exception")
            sys.exit(1)

if __name__ == "__main__":
    main()