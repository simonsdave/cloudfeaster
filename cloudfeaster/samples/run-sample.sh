#!/usr/bin/env bash

#
# ./run-sample.sh xe_exchange_rates
# ./run-sample.sh pypi "${PYPI_USERNAME}" "${PYPI_PASSWORD}"
# ./run-sample.sh pythonwheels
#

set -e

if [ $# -lt 1 ]; then
    echo "usage: $(basename "$0") <spider> [<arg1> <arg2> ... <argN>]" >&2
    exit 1
fi

SPIDER=${1:-}
shift

# export CLF_REMOTE_CHROMEDRIVER=http://host.docker.internal:9515
# https://docs.docker.com/docker-for-mac/networking/
NETWORK=bridge
if [ ! "${CLF_REMOTE_CHROMEDRIVER:-}" == "" ]; then NETWORK=host; fi

DOCKER_CONTAINER_NAME=$(python -c "import uuid; print uuid.uuid4().hex")

SPIDER_OUTPUT=$(mktemp 2> /dev/null || mktemp -t DAS)

docker run \
    --name "${DOCKER_CONTAINER_NAME}" \
    --security-opt seccomp:unconfined \
    --volume "$(repo-root-dir.sh):/app" \
    -e "CLF_REMOTE_CHROMEDRIVER=${CLF_REMOTE_CHROMEDRIVER:-}" \
    "--network=${NETWORK}" \
    "${DEV_ENV_DOCKER_IMAGE}" \
    /bin/bash -c "/app/$(repo.sh -u)/samples/${SPIDER}.py" "$@" >& "${SPIDER_OUTPUT}"

SPIDER_OUTPUT_ARTIFACT_DIR=$(mktemp -d 2> /dev/null || mktemp -d -t DAS)

CHROMEDRIVER_LOG_IN_CONTAINER=$(jq -r ._debug.chromeDriverLog "${SPIDER_OUTPUT}" | sed -e "s|null||g")
if [ ! "${CHROMEDRIVER_LOG_IN_CONTAINER}" == "" ]; then
    CHROMEDRIVER_LOG_ON_HOST=${SPIDER_OUTPUT_ARTIFACT_DIR}/$(basename "${CHROMEDRIVER_LOG_IN_CONTAINER}")

    docker container cp \
        "${DOCKER_CONTAINER_NAME}:${CHROMEDRIVER_LOG_IN_CONTAINER}" \
        "${CHROMEDRIVER_LOG_ON_HOST}"

    sed -i "" -e "s|${CHROMEDRIVER_LOG_IN_CONTAINER}|${CHROMEDRIVER_LOG_ON_HOST}|" "${SPIDER_OUTPUT}"
fi

docker container rm "${DOCKER_CONTAINER_NAME}" > /dev/null

cat "${SPIDER_OUTPUT}"

exit 0
