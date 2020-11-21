#!/usr/bin/env bash

#
# A repeated pattern emerge where a shell script need to parse
# setup.py and extract the cloudfeaster version. This script
# centralizes implementation of the pattern.
#

set -e

if [ $# != 0 ]; then
    echo "usage: $(basename "$0")" >&2
    exit 1
fi

grep cloudfeaster== "$(repo-root-dir.sh)/setup.py" | sed -e "s|^[[:space:]]*['\"]cloudfeaster==||g" | sed -e "s|['\"].*$||g"

exit 0
