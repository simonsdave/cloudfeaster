#!/usr/bin/env bash
#
# this script ...
#

set -e

if [ $# != 4 ]; then
    echo "usage: $(basename "$0") <image-name> <username> <password> <tag>" >&2
    exit 1
fi

IMAGENAME=${1:-}
USERNAME=${2:-}
PASSWORD=${3:-}
TAG=${4:-}

NEW_IMAGENAME=$USERNAME/cloudfeaster:$TAG

docker tag "$IMAGENAME" "$NEW_IMAGENAME"

docker login --username="$USERNAME" --password="$PASSWORD"
docker push "$NEW_IMAGENAME"

exit 0
