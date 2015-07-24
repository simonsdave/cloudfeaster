#!/usr/bin/env bash

# Execute this script to discover all the spiders that are
# available to run in a docker image.
#
# This script is a wrapper around spiders.py that simply seperates
# the responsibility of spider discovery (spiders.py) from saving
# the discovered spider results (spiders.sh).
#
# Assuming etcd is running, the follow will verify this script
# is working correctly:
#
# curl -s -L -o /dev/null -w "%{http_code}\n" http://127.0.0.1:4001/v2/keys/0456d10966d742eca749fc9226b77456
#   <<<should return 404>>>
# spiders.sh http://127.0.0.1:4001/v2/keys/0456d10966d742eca749fc9226b77456 20
#   <<<should return exit code of 0>>>
# curl -s -L -o /dev/null -w "%{http_code}\n" http://127.0.0.1:4001/v2/keys/0456d10966d742eca749fc9226b77456
#   <<<should return 200>>>
# curl -s -L http://127.0.0.1:4001/v2/keys/0456d10966d742eca749fc9226b77456
#   <<< should return {} or more if spider modules are installed>>>

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
