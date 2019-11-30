#!/usr/bin/env bash

#
# Usage Examples
#
#   Usual running of spiders
#
#       ./run-sample.sh xe_exchange_rates
#       ./run-sample.sh pypi "${PYPI_USERNAME}" "${PYPI_PASSWORD}"
#       ./run-sample.sh pythonwheels
#
#   Debugging
#
#       ./run-sample.sh --verbose xe_exchange_rates
#       ./run-sample.sh --debug xe_exchange_rates
#

usage() {
    echo "usage: $(basename "$0") [--verbose|--debug] <spider> [<arg1> <arg2> ... <argN>]" >&2
    return 0
}

VERBOSE=0
CLF_DEBUG=''

echo_if_verbose() {
    if [ "1" -eq "${VERBOSE:-0}" ]; then
        echo "$@"
    fi
    return 0
}

while true
do
    case "${1:-}" in
        --verbose)
            shift
            # can only use --verbose or --debug command line option
            if [ "1" -eq "${VERBOSE:-}" ]; then
                usage
                exit 1
            fi
            VERBOSE=1
            ;;
        --debug)
            shift
            # can only use --verbose or --debug command line option
            if [ "1" -eq "${VERBOSE:-}" ]; then
                usage
                exit 1
            fi
            VERBOSE=1
            CLF_DEBUG=DEBUG
            ;;
        --help)
            shift
            usage
            exit 0
            ;;
        *)
            break
            ;;
    esac
done

if [ $# -lt 1 ]; then
    usage
    exit 1
fi

SPIDER=${1:-}
shift

# export CLF_REMOTE_CHROMEDRIVER=http://host.docker.internal:9515
# https://docs.docker.com/docker-for-mac/networking/
NETWORK=bridge
if [ ! "${CLF_REMOTE_CHROMEDRIVER:-}" == "" ]; then NETWORK=host; fi

DOCKER_CONTAINER_NAME=$(python -c "import uuid; print uuid.uuid4().hex")

SPIDER_OUTPUT_ARTIFACT_DIR=$(mktemp -d 2> /dev/null || mktemp -d -t DAS)
echo_if_verbose "Spider output artifact directory @ '${SPIDER_OUTPUT_ARTIFACT_DIR}'"

SPIDER_OUTPUT=${SPIDER_OUTPUT_ARTIFACT_DIR}/spider-output.json

docker run \
    --name "${DOCKER_CONTAINER_NAME}" \
    --security-opt seccomp:unconfined \
    --volume "$(repo-root-dir.sh):/app" \
    -e "CLF_REMOTE_CHROMEDRIVER=${CLF_REMOTE_CHROMEDRIVER:-}" \
    -e "CLF_DEBUG=${CLF_DEBUG:-}" \
    "--network=${NETWORK}" \
    "${DEV_ENV_DOCKER_IMAGE}" \
    "/app/$(repo.sh -u)/samples/${SPIDER}.py" "$@" >& "${SPIDER_OUTPUT}"

SPIDER_LOG_IN_CONTAINER=$(jq -r ._debug.spiderLog "${SPIDER_OUTPUT}" | sed -e "s|null||g")
if [ ! "${SPIDER_LOG_IN_CONTAINER}" == "" ]; then
    SPIDER_LOG_ON_HOST=${SPIDER_OUTPUT_ARTIFACT_DIR}/spider-log.txt

    docker container cp \
        "${DOCKER_CONTAINER_NAME}:${SPIDER_LOG_IN_CONTAINER}" \
        "${SPIDER_LOG_ON_HOST}"

    sed -i "" -e "s|${SPIDER_LOG_IN_CONTAINER}|${SPIDER_LOG_ON_HOST}|" "${SPIDER_OUTPUT}"
fi

CHROMEDRIVER_LOG_IN_CONTAINER=$(jq -r ._debug.chromeDriverLog "${SPIDER_OUTPUT}" | sed -e "s|null||g")
if [ ! "${CHROMEDRIVER_LOG_IN_CONTAINER}" == "" ]; then
    CHROMEDRIVER_LOG_ON_HOST=${SPIDER_OUTPUT_ARTIFACT_DIR}/chromedriver-log.txt

    docker container cp \
        "${DOCKER_CONTAINER_NAME}:${CHROMEDRIVER_LOG_IN_CONTAINER}" \
        "${CHROMEDRIVER_LOG_ON_HOST}"

    sed -i "" -e "s|${CHROMEDRIVER_LOG_IN_CONTAINER}|${CHROMEDRIVER_LOG_ON_HOST}|" "${SPIDER_OUTPUT}"
fi

docker container rm "${DOCKER_CONTAINER_NAME}" > /dev/null

cat "${SPIDER_OUTPUT}"

exit 0
