#!/usr/bin/env bash

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

usage() {
    echo "usage: $(basename "$0") [--verbose]" >&2
}

VERBOSE=0

while true
do
    case "$(echo "${1:-}" | tr "[:upper:]" "[:lower:]")" in
        -v|--verbose)
            shift
            VERBOSE=1
            ;;
        -h|--help)
            shift
            usage
            exit 0
            ;;
        *)
            break
            ;;
    esac
done

if [ $# != 0 ]; then
    usage
    exit 1
fi

EXIT_CODE=0

for SPIDER_FILENAME in "$(repo-root-dir.sh)"/"$(repo.sh -u)"/*.py
do
    if [ ! -x "${SPIDER_FILENAME}" ]; then
        if [ "1" -eq "${VERBOSE:-0}" ]; then
            echo "ignoring '${SPIDER_FILENAME}'"
        fi
        continue
    fi

    echo "${SPIDER_FILENAME}"

    SPIDER_OUTPUT=$(mktemp 2> /dev/null || mktemp -t DAS)
    if ! "${SCRIPT_DIR_NAME}/run-spider.sh" "$(basename "${SPIDER_FILENAME}")" >& "${SPIDER_OUTPUT}"; then
        EXIT_CODE=1
        cat "${SPIDER_OUTPUT}"
    else
        if [ "1" -eq "${VERBOSE:-0}" ]; then
            cat "${SPIDER_OUTPUT}"
        fi
    fi
    rm "${SPIDER_OUTPUT}"
done

exit ${EXIT_CODE}
