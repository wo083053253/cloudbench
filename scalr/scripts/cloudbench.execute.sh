#!/bin/bash
set -o errexit
set -o nounset

cloudbench -c $CLOUDBENCH_CONFIG
