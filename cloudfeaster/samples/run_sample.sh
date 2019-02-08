#!/usr/bin/env bash

#
# ./run_sample.sh xe_exchange_rates.XEExchangeRatesSpider
# ./run_sample.sh pypi.PyPISpider <username> <password>
# ./run_sample.sh pythonwheels.PythonWheelsSpider
#

set -e

if [ $# -lt 1 ]; then
    echo "usage: $(basename "$0") <docker-image> <spider> [<arg1> <arg2> ... <argN>]" >&2
    exit 1
fi

SPIDER=${1:-}
shift

docker run \
    --rm \
    --security-opt seccomp:unconfined \
    --volume "$DEV_ENV_SOURCE_CODE:/app" \
    "$DEV_ENV_DOCKER_IMAGE" \
    spiderhost.sh "cloudfeaster.samples.$SPIDER" "$@"

exit 0
