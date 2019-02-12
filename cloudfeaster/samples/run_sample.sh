#!/usr/bin/env bash

#
# ./run_sample.sh xe_exchange_rates.XEExchangeRatesSpider
# ./run_sample.sh pypi.PyPISpider <username> <password>
# ./run_sample.sh pythonwheels.PythonWheelsSpider
#

set -e

NETWORK=bridge
REMOTE_CHROMEDRIVER=""

while true
do
    case "${1:-}" in
    # :TODO: how to deal with lower case variable substitution on mac os?
    # case "${1,,}" in
        -r)
            shift
            REMOTE_CHROMEDRIVER=${1:-}
            shift
            NETWORK=host
            ;;
        *)
            break
            ;;
    esac
done

if [ $# -lt 1 ]; then
    echo "usage: $(basename "$0") [-r <remote-chromedriver>] <docker-image> <spider> [<arg1> <arg2> ... <argN>]" >&2
    exit 1
fi

SPIDER=${1:-}
shift

docker run \
    --rm \
    --security-opt seccomp:unconfined \
    --volume "$DEV_ENV_SOURCE_CODE:/app" \
    -e "CLF_REMOTE_CHROMEDRIVER=$REMOTE_CHROMEDRIVER" \
    "--network=$NETWORK" \
    "$DEV_ENV_DOCKER_IMAGE" \
    spiderhost.sh "cloudfeaster.samples.$SPIDER" "$@"

exit 0
