#!/bin/bash
set -o errexit
set -o nounset


cat > $CLOUDBENCH_CONFIG << EOF
[environment]
nobench = $CLOUDBENCH_NOBENCH

[reporting]
endpoint = $CLOUDBENCH_ENDPOINT
username = $CLOUDBENCH_USERNAME
apikey = $CLOUDBENCH_API_KEY
retry_max = $CLOUDBENCH_RETRY_MAX
retry_wait = $CLOUDBENCH_RETRY_WAIT
retry_range = $CLOUDBENCH_RETRY_RANGE

[benchmarks]
blocksizes = $CLOUDBENCH_BLOCK_SIZES
depths = $CLOUDBENCH_DEPTHS
modes = $CLOUDBENCH_MODES
EOF
