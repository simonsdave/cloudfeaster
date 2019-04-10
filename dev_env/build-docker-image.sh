#!/usr/bin/env bash
#
# This script builds a docker image which packages up the
# development environment and associated tooling.
#

set -e

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

if [ $# != 1 ]; then
    echo "usage: $(basename "$0") <docker image name>" >&2
    exit 1
fi

DOCKER_IMAGE=${1:-}

TEMP_DOCKERFILE=$(mktemp 2> /dev/null || mktemp -t DAS)
cp "$SCRIPT_DIR_NAME/Dockerfile.template" "$TEMP_DOCKERFILE"

CONTEXT_DIR=$(mktemp -d 2> /dev/null || mktemp -d -t DAS)
pushd .. > /dev/null && tar cf "$CONTEXT_DIR/package.tar" . && popd > /dev/null

DEV_ENV_VERSION=$(cat "$SCRIPT_DIR_NAME/dev-env-version.txt")
if [ "${DEV_ENV_VERSION:-}" == "master" ]; then
    DEV_ENV_VERSION=latest
fi
sed \
    -i '' \
    -e "s|%DEV_ENV_VERSION%|$DEV_ENV_VERSION|g" \
    "$TEMP_DOCKERFILE"

PACKAGE=$(pushd .. > /dev/null; basename "$PWD"; popd > /dev/null)
PACKAGE=${PACKAGE//-/_}

docker build \
    -t "$DOCKER_IMAGE" \
    --file "$TEMP_DOCKERFILE" \
    --build-arg PACKAGE=dev_env \
    "$CONTEXT_DIR"

rm -rf "$CONTEXT_DIR"

exit 0
