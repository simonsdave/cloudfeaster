#!/usr/bin/env bash

set -e

if [ $# -lt 2 ]; then
    echo "usage: $(basename "$0") <docker-image> <spider> [<arg1> <arg2> ... <argN>]" >&2
    exit 1
fi

DOCKER_IMAGE=${1:-}
shift
SPIDER=${1:-}
shift

docker run \
    --rm \
    --security-opt seccomp:unconfined \
    "$DOCKER_IMAGE" \
    spiderhost.sh "cloudfeaster.samples.$SPIDER" "$@"

exit 0