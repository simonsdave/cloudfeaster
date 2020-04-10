#!/usr/bin/env bash
#
# This script builds Cloudfeaster's docker image
#

set -e
set -x

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

TEMP_DOCKERFILE=$(mktemp 2> /dev/null || mktemp -t DAS)
cp "${SCRIPT_DIR_NAME}/Dockerfile.template" "${TEMP_DOCKERFILE}"

sed \
    -i '' \
    -e "s|%CIRCLE_CI_EXECUTOR%|$(get-circle-ci-executor.sh)|g" \
    "${TEMP_DOCKERFILE}"

docker build \
    -t "${IMAGE_NAME}" \
    --file "${TEMP_DOCKERFILE}" \
    "${CONTEXT_DIR}"

rm -f "${TEMP_DOCKERFILE}"
rm -rf "${CONTEXT_DIR}"

exit 0
