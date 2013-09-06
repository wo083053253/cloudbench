**********
Cloudbench
**********

Cloudbench is a library designed to make Cloud benchmarking easier.

Cloudbench integrates with a web service (not yet publicly available) to upload
benchmark results, and compare your Cloud with other offerings.


-----
Usage
-----

First, define the configuration file for the benchmark:

.. code-block:: ini

    [environment]
    fio = Path to the fio binary [/usr/local/bin/fio]
    pidfile = Path to the pid file to use [var/run/cloudbench.pid]
    logfile = Path to the log file to use [/var/log/cloudbench.log]
    nobench = Comma-separated list of devices to not use in benchmark []

    [general]
    size = The size of the file to use in benchmarks [10G]
    ramp = The duration of the benchmark ramp time [15 seconds]
    duration = The duration of the benchmarks [600 seconds]

    [reporting]
    endpoint = The endpoint to report data to
    username = The username to authenticate with at the endpoint
    apikey = The API key to authenticate with at the endpoint

    [benchmarks]
    blocksizes = Comma-separated list of block sizes to use during benchmarking
    depths = Comma-separated list of depths to use during benchmarking
    modes = Comma-separated list of modes to use during benchmarking


Next, execute cloudbench and point it to your configuration file


.. code-block:: bash

    $ cloudbench -c /path/to/config/file.ini

By default, cloudbench looks for its config file in ``/etc/cloudbench.ini``


-------
License
-------

See LICENSE.
