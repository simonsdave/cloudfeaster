#!/usr/bin/env bash

set -e

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

if [ $# != 0 ]; then
    echo "usage: $(basename "$0")" >&2
    exit 1
fi

EXPECTED_CONFIG=$(mktemp 2> /dev/null || mktemp -t DAS)
"${SCRIPT_DIR_NAME}/generate-circleci-config.py" > "${EXPECTED_CONFIG}"
diff "${EXPECTED_CONFIG}" "$(repo-root-dir.sh)/.circleci/config.yml"
rm -f "${EXPECTED_CONFIG}"

exit 0
