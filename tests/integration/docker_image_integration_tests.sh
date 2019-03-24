#!/usr/bin/env bash

set -e

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

test_sample_spider() {
    SPIDER=${1:-}
    shift

    SAMPLES_DIR=$(docker run \
        --rm \
        --security-opt seccomp:unconfined \
        "$DOCKER_IMAGE" \
        python -c 'import cloudfeaster.samples, os; print os.path.dirname(cloudfeaster.samples.__file__)')

    STDOUT=$(mktemp)

    docker run \
        --rm \
        --security-opt seccomp:unconfined \
        "$DOCKER_IMAGE" \
        "$SAMPLES_DIR/$SPIDER.py" "$@" \
        > "$STDOUT"

    # check if spiderhost.sh output was valid json - jq's exit
    # status will be non-zero if it's not valid json
    jq . "$STDOUT" >& /dev/null

    # confirm spider executed successfully
    if [ "$(jq ._metadata.status.code "$STDOUT")" != "0" ]; then cat "$STDOUT" && exit 1; fi

    rm "$STDOUT"
}

test_sample_spider_python_wheels() {
    test_sample_spider pythonwheels
}

test_sample_spider_pypi() {
    test_sample_spider pypi "$PYPI_USERNAME" "$PYPI_PASSWORD"
}

test_sample_spider_xe_exchange_rates() {
    test_sample_spider xe_exchange_rates
}

test_wrapper() {
    TEST_FUNCTION_NAME=${1:-}
    NUMBER_TESTS_RUN=$((NUMBER_TESTS_RUN+1))
    echo -n "."
    "$TEST_FUNCTION_NAME"
}

if [ $# != 3 ]; then
    echo "usage: $(basename "$0") <docker image> <pypi username> <pypi password>" >&2
    exit 1
fi

DOCKER_IMAGE=${1:-}
PYPI_USERNAME=${2:-}
PYPI_PASSWORD=${3:-}

NUMBER_TESTS_RUN=0
test_wrapper test_sample_spider_python_wheels
test_wrapper test_sample_spider_pypi
test_wrapper test_sample_spider_xe_exchange_rates
echo ""
echo "Successfully completed $NUMBER_TESTS_RUN integration tests."

exit 0
