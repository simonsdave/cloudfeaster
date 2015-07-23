#!/usr/bin/env bash

set -x
# Execute this script to discover all the spiders that are
# available to run in a docker image.
#
# This script is a wrapper around spiders.py that simply seperates
# the responsibility of spider discovery (spiders.py) from saving
# the discovered spider results (spiders.sh).

if [ $# -ne 2 ]; then
    echo "usage: `basename $0` <output url> <ttl>" >&2
    exit 1
fi

OUTPUT_URL=$1
TTL=$2

OUTPUT=$(mktemp 2> /dev/null || mktemp -t DAS)
spiders.py >& "$OUTPUT"
if [ "$?" != "0" ]; then
    exit 1
fi

HTTP_STATUS_CODE=$(curl -s -L -o /dev/null -w "%{http_code}" -X PUT --data-urlencode value@$OUTPUT -d ttl=$TTL $OUTPUT_URL)
if [ "$?" != "0" ] || [ "$HTTP_STATUS_CODE" != "201" ]; then
    exit 2
fi

exit 0
