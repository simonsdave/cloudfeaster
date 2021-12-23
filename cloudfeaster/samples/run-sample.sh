#!/usr/bin/env bash

#
# Usage Examples
#
#   Usual running of spiders
#
#       ./run-sample.sh xe_exchange_rates.py
#       ./run-sample.sh pypi.py "${PYPI_USERNAME}" "${PYPI_PASSWORD}"
#       ./run-sample.sh pythonwheels.py
#
#   Debugging
#
#       ./run-sample.sh --verbose xe_exchange_rates.py
#       ./run-sample.sh --debug xe_exchange_rates.py
#

copy_debug_files_from_container_to_host() {
    DOCKER_CONTAINER_NAME=${1:-}
    CRAWL_OUTPUT=${2:-}
    KEY=${3:-}
    CRAWL_OUTPUT_ARTIFACT_DIR=${4:-}
    HOST_FILENAME=${5:-}

    DEBUG_FILE_IN_CONTAINER=$(jq -r "._debug.${KEY}" "${CRAWL_OUTPUT}" | sed -e "s|null||g")
    if [ ! "${DEBUG_FILE_IN_CONTAINER}" == "" ]; then
        DEBUG_FILE_ON_HOST=${CRAWL_OUTPUT_ARTIFACT_DIR}/${HOST_FILENAME}

        docker container cp \
            "${DOCKER_CONTAINER_NAME}:${DEBUG_FILE_IN_CONTAINER}" \
            "${DEBUG_FILE_ON_HOST}"

        sed -i "" -e "s|${DEBUG_FILE_IN_CONTAINER}|${DEBUG_FILE_ON_HOST}|" "${CRAWL_OUTPUT}"
    fi

    return 0
}

usage() {
    echo "usage: $(basename "$0") [--inline] [--pretty] [--verbose|--debug] <spider> [<arg1> <arg2> ... <argN>]" >&2
    return 0
}

VERBOSE=0
PRETTY=0
CLF_DEBUG=''
CLF_INLINE_DEBUG=''

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
        --pretty)
            shift
            PRETTY=1
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
        --inline)
            shift
            CLF_INLINE_DEBUG=1
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

DOCKER_CONTAINER_NAME=$(openssl rand -hex 16)

CRAWL_OUTPUT_ARTIFACT_DIR=$(mktemp -d 2> /dev/null || mktemp -d -t DAS)
echo_if_verbose "Spider output artifact directory @ '${CRAWL_OUTPUT_ARTIFACT_DIR}'"

CRAWL_OUTPUT=${CRAWL_OUTPUT_ARTIFACT_DIR}/crawl-output.json

docker run \
    --name "${DOCKER_CONTAINER_NAME}" \
    --security-opt seccomp:unconfined \
    --volume "$(repo-root-dir.sh):/app" \
    -e "CLF_REMOTE_CHROMEDRIVER=${CLF_REMOTE_CHROMEDRIVER:-}" \
    -e "CLF_DEBUG=${CLF_DEBUG:-}" \
    -e "CLF_INLINE_DEBUG=${CLF_INLINE_DEBUG:-}" \
    "--network=${NETWORK}" \
    "${DEV_ENV_DOCKER_IMAGE}" \
    "/app/$(repo.sh -u)/samples/${SPIDER}" "$@" >& "${CRAWL_OUTPUT}"

if [[ "${CLF_INLINE_DEBUG:-}" == "" ]]; then
    copy_debug_files_from_container_to_host \
        "${DOCKER_CONTAINER_NAME}" \
        "${CRAWL_OUTPUT}" \
        'crawlLog' \
        "${CRAWL_OUTPUT_ARTIFACT_DIR}" \
        'crawl-log.txt'

    copy_debug_files_from_container_to_host \
        "${DOCKER_CONTAINER_NAME}" \
        "${CRAWL_OUTPUT}" \
        'chromeDriverLog' \
        "${CRAWL_OUTPUT_ARTIFACT_DIR}" \
        'chromedriver-log.txt'

    copy_debug_files_from_container_to_host \
        "${DOCKER_CONTAINER_NAME}" \
        "${CRAWL_OUTPUT}" \
        'screenshot' \
        "${CRAWL_OUTPUT_ARTIFACT_DIR}" \
        'screenshot.png'
fi

docker container rm "${DOCKER_CONTAINER_NAME}" > /dev/null

if [[ "${PRETTY:-}" == "0" ]]; then
    cat "${CRAWL_OUTPUT}"
else
    jq . "${CRAWL_OUTPUT}"
fi

exit 0
