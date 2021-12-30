#!/usr/bin/env bash

usage() {
    echo "usage: $(basename "$0") [--verbose] [--output <dir>] <docker image> <pypi username> <pypi password>" >&2
}

copy_debug_files_from_container_to_host() {
    DOCKER_CONTAINER_NAME=${1:-}
    CRAWL_OUTPUT=${2:-}
    KEY=${3:-}
    ARTIFACT_DIR=${4:-}
    HOST_FILENAME=${5:-}

    DEBUG_FILE_IN_CONTAINER=$(jq -r "._debug.${KEY}" "${CRAWL_OUTPUT}" | sed -e "s|null||g")
    if [ ! "${DEBUG_FILE_IN_CONTAINER}" == "" ]; then
        DEBUG_FILE_ON_HOST=${ARTIFACT_DIR}/${HOST_FILENAME}

        docker container cp \
            "${DOCKER_CONTAINER_NAME}:${DEBUG_FILE_IN_CONTAINER}" \
            "${DEBUG_FILE_ON_HOST}"

        sed -i -e "s|${DEBUG_FILE_IN_CONTAINER}|${DEBUG_FILE_ON_HOST}|" "${CRAWL_OUTPUT}"
    fi

    return 0
}

test_sample_spider() {
    SPIDER=${1:-}
    shift

    SAMPLES_DIR=$(docker run \
        --rm \
        "${DOCKER_IMAGE}" \
        python3.9 -c 'import cloudfeaster.samples, os; print(os.path.dirname(cloudfeaster.samples.__file__))')

    DOCKER_CONTAINER_NAME=$(openssl rand -hex 16)

    CRAWL_OUTPUT=$(mktemp)

    docker run \
        --name "${DOCKER_CONTAINER_NAME}" \
        "${DOCKER_IMAGE}" \
        "${SAMPLES_DIR}/${SPIDER}.py" "$@" \
        > "${CRAWL_OUTPUT}"

    # {"_metadata":{"status":{"code":500,"message": "crawl output was not json"}}
    if ! jq . "${CRAWL_OUTPUT}" >& /dev/null; then
        true
    fi

    if [[ "${CRAWL_OUTPUT_ARTIFACT_DIR}" != "" ]]; then
        SPIDER_CRAWL_OUTPUT_ARTIFACT_DIR=${CRAWL_OUTPUT_ARTIFACT_DIR}/${SPIDER}

        mkdir -p "${SPIDER_CRAWL_OUTPUT_ARTIFACT_DIR}"

        copy_debug_files_from_container_to_host \
            "${DOCKER_CONTAINER_NAME}" \
            "${CRAWL_OUTPUT}" \
            'crawlLog' \
            "${SPIDER_CRAWL_OUTPUT_ARTIFACT_DIR}" \
            'crawl-log.txt'

        copy_debug_files_from_container_to_host \
            "${DOCKER_CONTAINER_NAME}" \
            "${CRAWL_OUTPUT}" \
            'chromeDriverLog' \
            "${SPIDER_CRAWL_OUTPUT_ARTIFACT_DIR}" \
            'chromedriver-log.txt'

        copy_debug_files_from_container_to_host \
            "${DOCKER_CONTAINER_NAME}" \
            "${CRAWL_OUTPUT}" \
            'screenshot' \
            "${SPIDER_CRAWL_OUTPUT_ARTIFACT_DIR}" \
            'screenshot.png'

        cp "${CRAWL_OUTPUT}" "${SPIDER_CRAWL_OUTPUT_ARTIFACT_DIR}/crawl-output.json"
    fi

    if [ "$(jq ._metadata.status.code "${CRAWL_OUTPUT}")" ==  "0" ]; then
        NUMBER_TESTS_PASS=$((NUMBER_TESTS_PASS+1))
        echo -n "pass"
    else
        echo -n "fail"
    fi

    docker container rm "${DOCKER_CONTAINER_NAME}" > /dev/null

    rm "${CRAWL_OUTPUT}"
}

test_sample_spider_alpine_releases() {
    test_sample_spider alpine_releases
}

test_sample_spider_pypi() {
    test_sample_spider pypi "${PYPI_USERNAME}" "${PYPI_PASSWORD}"
}

test_sample_spider_python_wheels() {
    test_sample_spider pythonwheels
}

test_sample_spider_xe_exchange_rates() {
    test_sample_spider xe_exchange_rates
}

test_wrapper() {
    TEST_FUNCTION_NAME=${1:-}
    NUMBER_TESTS_RUN=$((NUMBER_TESTS_RUN+1))
    if [ "1" -eq "${VERBOSE:-0}" ]; then
        echo -n "Running #${NUMBER_TESTS_RUN} '${TEST_FUNCTION_NAME}' ... "
    fi
    "${TEST_FUNCTION_NAME}"
    echo ""
}

VERBOSE=0
CRAWL_OUTPUT_ARTIFACT_DIR=""

while true
do
    case "${1:-}" in
        --output)
            shift
            CRAWL_OUTPUT_ARTIFACT_DIR=${1:-}
            shift
            ;;
        --help)
            shift
            usage
            exit 0
            ;;
        --verbose)
            shift
            VERBOSE=1
            ;;
        *)
            break
            ;;
    esac
done

if [ $# != 3 ]; then
    echo "usage: $(basename "$0") [--verbose] <docker image> <pypi username> <pypi password>" >&2
    exit 1
fi

DOCKER_IMAGE=${1:-}
PYPI_USERNAME=${2:-}
PYPI_PASSWORD=${3:-}

if [ "1" -eq "${VERBOSE:-0}" ]; then
    echo "Testing docker image '${DOCKER_IMAGE}'"
    echo "pypi username sha256:$(echo -n "${PYPI_USERNAME}" | openssl dgst -sha256)"
    echo "pypi password sha256:$(echo -n "${PYPI_PASSWORD}" | openssl dgst -sha256)"
fi

NUMBER_TESTS_RUN=0
NUMBER_TESTS_PASS=0
test_wrapper test_sample_spider_alpine_releases
test_wrapper test_sample_spider_pypi
test_wrapper test_sample_spider_python_wheels
test_wrapper test_sample_spider_xe_exchange_rates
if [ "1" -ne "${VERBOSE:-0}" ]; then
    echo ""
fi
echo "Completed ${NUMBER_TESTS_RUN} integration tests. ${NUMBER_TESTS_PASS} tests passed."

exit 0
