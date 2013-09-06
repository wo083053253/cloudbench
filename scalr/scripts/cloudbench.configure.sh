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

[benchmarks]
blocksizes = $CLOUDBENCH_BLOCK_SIZES
depths = $CLOUDBENCH_DEPTHS
modes = $CLOUDBENCH_MODES
EOF