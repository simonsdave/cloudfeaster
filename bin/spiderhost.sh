#!/usr/bin/env bash

# Execute this script to run a spider inside a docker container.
#
# This script is a wrapper around spiderhost.py that simply makes
# sure Xvfb is running before spiderhost.py executes and also wraps
# the interaction with etcd to store the results of running the
# spider.

if [ $# -ne 4 ]; then
    echo "usage: `basename $0` <spider output url> <spider> <args> <ttl>" >&2
    exit 1
fi

SPIDER_OUTPUT_URL=$1
SPIDER=$2
#
# :TRICKY: The odd if statement below is here because when Fleet runs this
# script and args is a zero length string, Fleet seems to get confused and
# not supply the right number of arguments. So, the checking for ----- is
# there to ensure that Fleet is never put in the position where it has to
# pass an argument that's zero length.
#
if [ "-----" == "$3" ]; then
    ARGS=""
else
    ARGS=$3
fi
TTL=$4

if [ "Linux" == "$(uname -s)" ]; then
    if [ "" == "$DISPLAY" ]; then
        export DISPLAY=:99
    fi
    if [ "0" == "`ps aux | grep \[X\]vfb | wc -l | sed -e "s/[[:space:]]//g"`" ]; then
        Xvfb $DISPLAY -ac -screen 0 1280x1024x24 >& /dev/null &
    fi
fi

SPIDER_OUTPUT=$(mktemp 2> /dev/null || mktemp -t DAS)
spiderhost.py --spider="$SPIDER" --args="$ARGS" >& "$SPIDER_OUTPUT"
if [ "$?" != "0" ]; then
    exit 2
fi

HTTP_STATUS_CODE=$(curl -s -L -o /dev/null -w "%{http_code}" -X PUT --data-urlencode value@$SPIDER_OUTPUT -d ttl=$TTL $SPIDER_OUTPUT_URL)
if [ "$?" != "0" ] || [ "$HTTP_STATUS_CODE" != "201" ]; then
    exit 3
fi

exit 0
