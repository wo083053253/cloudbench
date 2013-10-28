#!/bin/bash
set -o errexit
set -o nounset

apt-get update
apt-get install -y python-setuptools python-pip curl bzip2 build-essential libaio-dev

pip uninstall --yes python-novaclient || true
pip install lockfile boto pyrax cloudbench

FIO_BUILD=/tmp/$$-build/

mkdir -p $FIO_BUILD
cd $FIO_BUILD
curl --silent http://brick.kernel.dk/snaps/fio-2.0.15.tar.bz2 > fio-2.0.15.tar.bz2
bunzip2 fio-2.0.15.tar.bz2
tar -xf fio-2.0.15.tar
cd fio-2.0.15
make
make install
