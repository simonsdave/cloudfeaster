#!/usr/bin/env bash

#
# run_spider.sh miniclip.py
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
    echo "usage: $(basename "$0") <spider> [<arg1> <arg2> ... <argN>]" >&2
}

if [ $# -lt 1 ]; then
    usage
    exit 1
fi

while true
do
    case "${1:-}" in
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

SPIDER=${1:-}
shift

# CLF_REMOTE_CHROMEDRIVER=http://host.docker.internal:9515
# https://docs.docker.com/docker-for-mac/networking/
NETWORK=bridge
if [ ! "${CLF_REMOTE_CHROMEDRIVER:-}" == "" ]; then NETWORK=host; fi

DOCKER_CONTAINER_NAME=$(openssl rand -hex 16)

CRAWL_OUTPUT_ARTIFACT_DIR=$(mktemp -d 2> /dev/null || mktemp -d -t DAS)

CRAWL_OUTPUT=${CRAWL_OUTPUT_ARTIFACT_DIR}/crawl-output.json

docker run \
    --name "${DOCKER_CONTAINER_NAME}" \
    --security-opt seccomp:unconfined \
    --volume "$(repo-root-dir.sh):/app" \
    -e "CLF_REMOTE_CHROMEDRIVER=${CLF_REMOTE_CHROMEDRIVER:-}" \
    -e "CLF_DEBUG=${CLF_DEBUG:-}" \
    "--network=${NETWORK}" \
    "${DEV_ENV_DOCKER_IMAGE}" \
    "/app/$(repo.sh -u)/${SPIDER}" "$@" >& "${CRAWL_OUTPUT}"
EXIT_CODE=$?

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

docker container rm "${DOCKER_CONTAINER_NAME}" > /dev/null

cat "${CRAWL_OUTPUT}"

exit ${EXIT_CODE}
