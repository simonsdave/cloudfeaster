#!/usr/bin/env bash
#
# This script builds Cloudfeaster's docker image
#

set -e

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

if [ $# != 2 ]; then
    echo "usage: $(basename "$0") <cloudfeaster-tar-gz> <image-name>" >&2
    exit 1
fi

CLOUDFEASTER_TAR_GZ=${1:-}
IMAGE_NAME=${2:-}

CONTEXT_DIR=$(mktemp -d 2> /dev/null || mktemp -d -t DAS)

TEMP_DOCKERFILE=$CONTEXT_DIR/Dockerfile
cp "$SCRIPT_DIR_NAME/Dockerfile.template" "$TEMP_DOCKERFILE"

CHROMEDRIVER_VERSION=$(grep __chromedriver_version__ "$SCRIPT_DIR_NAME/../cloudfeaster/__init__.py" | sed -e "s|^.*=[[:space:]]*['\"]||g" | sed -e "s|['\"].*$||g")
sed \
    -i \
    -e "s|%CHROMEDRIVER_VERSION%|$CHROMEDRIVER_VERSION|g" \
    "$TEMP_DOCKERFILE"

cp "$CLOUDFEASTER_TAR_GZ" "$CONTEXT_DIR/cloudfeaster.tar.gz"
docker build -t "$IMAGE_NAME" --file "$TEMP_DOCKERFILE" "$CONTEXT_DIR"

rm -rf "$CONTEXT_DIR"

exit 0
