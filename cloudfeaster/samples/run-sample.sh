#!/usr/bin/env bash

#
# ./run-sample.sh xe_exchange_rates
# ./run-sample.sh pypi "$PYPI_USERNAME" "$PYPI_PASSWORD"
# ./run-sample.sh pythonwheels
#

set -e

if [ $# -lt 1 ]; then
    echo "usage: $(basename "$0") <spider> [<arg1> <arg2> ... <argN>]" >&2
    exit 1
fi

SPIDER=${1:-}
shift

# CLF_REMOTE_CHROMEDRIVER=http://host.docker.internal:9515
# https://docs.docker.com/docker-for-mac/networking/
NETWORK=bridge
if [ ! "${CLF_REMOTE_CHROMEDRIVER:-}" == "" ]; then NETWORK=host; fi

docker run \
    --rm \
    --security-opt seccomp:unconfined \
    --volume "$(repo-root-dir.sh):/app" \
    -e "CLF_REMOTE_CHROMEDRIVER=$CLF_REMOTE_CHROMEDRIVER" \
    "--network=$NETWORK" \
    "$DEV_ENV_DOCKER_IMAGE" \
    "/app/$(repo.sh -u)/samples/$SPIDER.py" "$@"

exit 0
