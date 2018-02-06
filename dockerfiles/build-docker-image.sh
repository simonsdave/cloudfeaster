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

cp "$CLOUDFEASTER_TAR_GZ" "$SCRIPT_DIR_NAME/cloudfeaster.tar.gz"
docker build -t "$IMAGE_NAME" "$SCRIPT_DIR_NAME"
rm "$SCRIPT_DIR_NAME/cloudfeaster.tar.gz"

exit 0
