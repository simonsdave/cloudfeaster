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

TEMP_DOCKERFILE=$(mktemp)
cp "$SCRIPT_DIR_NAME/Dockerfile.template" "$TEMP_DOCKERFILE"

CHROMEDRIVER_VERSION=$(grep __chromedriver_version__ "$SCRIPT_DIR_NAME/../cloudfeaster/__init__.py" | sed -e "s|^.*=[[:space:]]*['\"]||g" | sed -e "s|['\"].*$||g")
sed \
    -i \
    -e "s|%CHROMEDRIVER_VERSION%|$CHROMEDRIVER_VERSION|g" \
    "$TEMP_DOCKERFILE"

cp "$CLOUDFEASTER_TAR_GZ" "$SCRIPT_DIR_NAME/cloudfeaster.tar.gz"
docker build -t "$IMAGE_NAME" --file "$TEMP_DOCKERFILE" "$SCRIPT_DIR_NAME"
rm "$SCRIPT_DIR_NAME/cloudfeaster.tar.gz"

exit 0
