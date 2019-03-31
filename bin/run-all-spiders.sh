#!/usr/bin/env bash

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

VERBOSE=0

while true
do
    case "$(echo "${1:-}" | tr "[:upper:]" "[:lower:]")" in
        -v)
            shift
            VERBOSE=1
            ;;
        *)
            break
            ;;
    esac
done

if [ $# != 0 ]; then
    echo "usage: $(basename "$0") [-v]" >&2
    exit 1
fi

EXIT_CODE=0

for SPIDER_FILENAME in "$(repo-root-dir.sh)"/"$(repo.sh -u)"/*.py
do
    if [ ! -x "$SPIDER_FILENAME" ]; then
        if [ "1" -eq "${VERBOSE:-0}" ]; then
            echo "ignoring '$SPIDER_FILENAME'"
        fi
        continue
    fi

    SPIDER_NAME=$(basename "${SPIDER_FILENAME/.py/}")
    echo "$SPIDER_NAME"

    SPIDER_OUTPUT=$(mktemp 2> /dev/null || mktemp -t DAS)
    if ! "$SCRIPT_DIR_NAME/run-spider.sh" "$SPIDER_NAME" >& "$SPIDER_OUTPUT"; then
        EXIT_CODE=1
        cat "$SPIDER_OUTPUT"
    fi
    rm "$SPIDER_OUTPUT"
done

exit $EXIT_CODE
