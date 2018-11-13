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

CONTEXT_DIR=$(mktemp -d 2> /dev/null || mktemp -d -t DAS)
PROJECT_HOME_DIR="$SCRIPT_DIR_NAME/.."
cp "$PROJECT_HOME_DIR/requirements.txt" "$CONTEXT_DIR/."
cp "$PROJECT_HOME_DIR/setup.py" "$CONTEXT_DIR/."
mkdir "$CONTEXT_DIR/cloudfeaster"
cp "$PROJECT_HOME_DIR/cloudfeaster/__init__.py" "$CONTEXT_DIR/cloudfeaster/."
mkdir "$CONTEXT_DIR/cloudfeaster/samples"
cp "$PROJECT_HOME_DIR/cloudfeaster/samples/__init__.py" "$CONTEXT_DIR/cloudfeaster/samples/."
mkdir "$CONTEXT_DIR/bin"
cp "$PROJECT_HOME_DIR/bin/spiderhost.sh" "$CONTEXT_DIR/bin/."
cp "$PROJECT_HOME_DIR/bin/spiderhost.py" "$CONTEXT_DIR/bin/."
cp "$PROJECT_HOME_DIR/bin/spiders.sh" "$CONTEXT_DIR/bin/."
cp "$PROJECT_HOME_DIR/bin/spiders.py" "$CONTEXT_DIR/bin/."

DEV_ENV_VERSION=$(cat "$SCRIPT_DIR_NAME/dev-env-version.txt")

TEMP_DOCKERFILE=$CONTEXT_DIR/Dockerfile
cp "$SCRIPT_DIR_NAME/Dockerfile.template" "$TEMP_DOCKERFILE"
sed \
    -i \
    -e "s|%DEV_ENV_VERSION%|$DEV_ENV_VERSION|g" \
    "$TEMP_DOCKERFILE"

docker build \
    -t "$DOCKER_IMAGE" \
    --file "$TEMP_DOCKERFILE" \
    "$CONTEXT_DIR"

rm -rf "$CONTEXT_DIR"

exit 0
