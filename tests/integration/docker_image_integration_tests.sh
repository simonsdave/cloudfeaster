#!/usr/bin/env bash

set -e

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

compare_two_json_files() {
    ONE=${1:-}
    TWO=${2:-}

    diff <(jq -S . "$ONE") <(jq -S . "$TWO")
}

test_spiders_dot_star_without_samples() {
    SCRIPT=${1:-}

    STDOUT=$(mktemp)

    docker run \
        --rm \
        "$DOCKER_IMAGE" \
        "$SCRIPT" \
        > "$STDOUT"

    compare_two_json_files \
        "$STDOUT" \
        "$SCRIPT_DIR_NAME/data/test_spiders_dot_star_without_samples_stdout.json"

    rm "$STDOUT"
}

test_spiders_dot_sh_without_samples() {
    test_spiders_dot_star_without_samples "spiders.sh"
}

test_spiders_dot_py_without_samples() {
    test_spiders_dot_star_without_samples "spiders.py"
}

test_spiders_dot_star_with_samples() {
    SCRIPT=${1:-}

    STDOUT=$(mktemp)

    docker run \
        --rm \
        "$DOCKER_IMAGE" \
        "$SCRIPT" "--samples" \
        > "$STDOUT"

    rm "$STDOUT"
}

test_spiders_dot_sh_with_samples() {
    test_spiders_dot_star_with_samples "spiders.sh"
}

test_spiders_dot_py_with_samples() {
    test_spiders_dot_star_with_samples "spiders.py"
}

test_sample_spider() {
    SPIDER=${1:-}
    shift

    STDOUT=$(mktemp)

    docker run \
        --rm \
        --security-opt seccomp:unconfined \
        "$DOCKER_IMAGE" \
        spiderhost.sh "cloudfeaster.samples.$SPIDER" "$@" \
        > "$STDOUT"

    # check if spiderhost.sh output was valid json - jq's exit
    # status will be non-zero if it's not valid json
    jq . "$STDOUT" >& /dev/null

    # confirm spider executed successfully
    if [ "$(jq ._metadata.status.code "$STDOUT")" != "0" ]; then cat "$STDOUT" && exit 1; fi

    rm "$STDOUT"
}

test_sample_spider_python_wheels() {
    test_sample_spider pythonwheels.PythonWheelsSpider
}

test_sample_spider_pypi() {
    test_sample_spider pypi.PyPISpider "$PYPI_USERNAME" "$PYPI_PASSWORD"
}

test_sample_spider_xe_exchange_rates() {
    test_sample_spider xe_exchange_rates.XEExchangeRatesSpider
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
test_wrapper test_spiders_dot_sh_without_samples
test_wrapper test_spiders_dot_py_without_samples
test_wrapper test_spiders_dot_sh_with_samples
test_wrapper test_spiders_dot_py_with_samples
test_wrapper test_sample_spider_python_wheels
test_wrapper test_sample_spider_pypi
test_wrapper test_sample_spider_xe_exchange_rates
echo ""
echo "Successfully completed $NUMBER_TESTS_RUN integration tests."

exit 0
