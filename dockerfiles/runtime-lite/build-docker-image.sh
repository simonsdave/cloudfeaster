#!/usr/bin/env bash

set -e

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

if [ $# != 2 ]; then
    echo "usage: $(basename "$0") <cloudfeaster-tar-gz> <image-name>" >&2
    exit 1
fi

CLOUDFEASTER_TAR_GZ=${1:-}
IMAGE_NAME=${2:-}

REPO_ROOT_DIR=$(repo-root-dir.sh)

CONTEXT_DIR=$(mktemp -d 2> /dev/null || mktemp -d -t DAS)
cp "${REPO_ROOT_DIR}/bin/install-chrome.sh" "${CONTEXT_DIR}/."
cp "${REPO_ROOT_DIR}/bin/install-chromedriver.sh" "${CONTEXT_DIR}/."
cp "${CLOUDFEASTER_TAR_GZ}" "${CONTEXT_DIR}/cloudfeaster.tar.gz"

docker build \
    -t "${IMAGE_NAME}" \
    --file "${SCRIPT_DIR_NAME}/Dockerfile" \
    "${CONTEXT_DIR}"

rm -f "${TEMP_DOCKERFILE}"
rm -rf "${CONTEXT_DIR}"

exit 0
