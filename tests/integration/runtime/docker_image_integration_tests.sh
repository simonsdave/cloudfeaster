#!/usr/bin/env bash

test_spiders_dot_py() {
    DOCKER_IMAGE=${1:-}
    shift

    STDOUT=$(mktemp)

    DOCKER_CONTAINER_NAME=$(openssl rand -hex 16)

    docker run \
        --name "${DOCKER_CONTAINER_NAME}" \
        "${DOCKER_IMAGE}" \
        spiders.py \
        > "${STDOUT}"

    if [ "$(docker container inspect "${DOCKER_CONTAINER_NAME}" | jq '.[0].State.ExitCode')" != "0" ]; then cat "${STDOUT}" && exit 1; fi

    jq . "${STDOUT}" >& /dev/null || { exit 1; }

    docker container rm "${DOCKER_CONTAINER_NAME}" > /dev/null

    rm "${STDOUT}"
}

test_wrapper() {
    TEST_FUNCTION_NAME=${1:-}
    shift
    NUMBER_TESTS_RUN=$((NUMBER_TESTS_RUN+1))
    if [ "1" -eq "${VERBOSE:-0}" ]; then
        echo "Running #${NUMBER_TESTS_RUN} '${TEST_FUNCTION_NAME}'"
    else
        echo -n "."
    fi
    "$TEST_FUNCTION_NAME" "$@"
}

VERBOSE=0

while true
do
    case "${1:-}" in
        --verbose)
            shift
            VERBOSE=1
            ;;
        *)
            break
            ;;
    esac
done

if [ $# != 1 ]; then
    echo "usage: $(basename "$0") [--verbose] <docker image>" >&2
    exit 1
fi

DOCKER_IMAGE=${1:-}

if [ "1" -eq "${VERBOSE:-0}" ]; then
    echo "Testing docker image '${DOCKER_IMAGE}'"
fi

NUMBER_TESTS_RUN=0
test_wrapper test_spiders_dot_py "${DOCKER_IMAGE}"
if [ "1" -ne "${VERBOSE:-0}" ]; then
    echo ""
fi
echo "Successfully completed $NUMBER_TESTS_RUN integration tests."

exit 0
