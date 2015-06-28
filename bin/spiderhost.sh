#!/usr/bin/env bash

# Execute this script to run a spider inside a docker container.
# This script is a wrapper around spiderhost.py that simply makes
# sure Xvfb is running before spiderhost.py executes.

if [ $# -lt 2 ]; then
    echo "usage: `basename $0` <spider output url> <spider> [arg1 arg2 ... argn]" >&2
    exit 1
fi

SPIDER_OUTPUT_URL=$1
SPIDER=$2
shift
shift

if [ "Linux" == "$(uname -s)" ]; then
    if [ "" == "$DISPLAY" ]; then
        export DISPLAY=:99
    fi
    if [ "0" == "`ps aux | grep \[X\]vfb | wc -l | sed -e "s/[[:space:]]//g"`" ]; then
        Xvfb $DISPLAY -ac -screen 0 1280x1024x24 >& /dev/null &
    fi
fi

SPIDER_OUTPUT=$(mktemp 2> /dev/null || mktemp -t DAS)
spiderhost.py --spider="$SPIDER" "$@" >& "$SPIDER_OUTPUT"
EXIT_CODE=$?

curl -L -X PUT --data-urlencode value@$SPIDER_OUTPUT "$SPIDER_OUTPUT_URL"

exit $EXIT_CODE
