#!/usr/bin/env bash

set -e

if [ $# != 4 ]; then
    echo "usage: $(basename "$0") <image-name> <tag> <username> <password>" >&2
    exit 1
fi

IMAGE_NAME=${1:-}
TAG=${2:-}
USERNAME=${3:-}
PASSWORD=${4:-}

NEW_IMAGE_NAME=${IMAGE_NAME/:*/:$TAG}

docker tag "$IMAGE_NAME" "$NEW_IMAGE_NAME"

echo "$PASSWORD" | docker login --username="$USERNAME" --password-stdin
docker push "$NEW_IMAGE_NAME"

exit 0
