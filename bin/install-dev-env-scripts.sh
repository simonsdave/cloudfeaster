#!/usr/bin/env bash

#
# should be run out of the spider repo - typically expect cfg4dev
# master will maintain reasonble backward compatibility
#
# curl -s -L "https://raw.githubusercontent.com/simonsdave/cloudfeaster/master/bin/install-dev-env-scripts.sh" | bash -s --
#

download_script() {
    CLF_VERSION=${1:-}
    SCRIPT=${2:-}

    DEST_SCRIPT=${VIRTUAL_ENV}/bin/${SCRIPT}

    curl \
       -s \
       -L \
       -o "${DEST_SCRIPT}" \
       "https://raw.githubusercontent.com/simonsdave/cloudfeaster/v${CLF_VERSION}/bin/${SCRIPT}"

    chmod u+x "${DEST_SCRIPT}"

    return 0
}

set -e

if [ $# != 0 ]; then
    echo "usage: $(basename "$0")" >&2
    exit 1
fi

if [ "${VIRTUAL_ENV:-}" == "" ]; then
    echo "Virtual env not activated - could not find environment variable VIRTUAL_ENV" >&2
    exit 2
fi

REPO_ROOT_DIR=$(git rev-parse --show-toplevel)
CLF_VERSION=$(grep cloudfeaster== "${REPO_ROOT_DIR}/setup.py" | sed -e "s|^[[:space:]]*['\"]cloudfeaster==||g" | sed -e "s|['\"].*$||g")

DEV_ENV_VERSION=$(curl -s -L "https://raw.githubusercontent.com/simonsdave/cloudfeaster/v${CLF_VERSION}/.circleci/config.yml" | grep 'image:' | tail -1 | sed -e 's|[[:space:]]*$||g' | sed -e 's|^.*dev-env:||g')
if [ "${DEV_ENV_VERSION}" == "latest" ]; then DEV_ENV_VERSION=master; fi
INSTALL_DEV_ENV=$(mktemp 2> /dev/null || mktemp -t DAS)
curl -s -L https://raw.githubusercontent.com/simonsdave/dev-env/${DEV_ENV_VERSION}/bin/install-dev-env.sh -o "${INSTALL_DEV_ENV}"
chmod a+x "${INSTALL_DEV_ENV}"
"${INSTALL_DEV_ENV}" --dev-env-version "${DEV_ENV_VERSION:-}"
rm "${INSTALL_DEV_ENV}"

download_script "${CLF_VERSION}" "run-all-spiders.sh"
download_script "${CLF_VERSION}" "run-spider.sh"
download_script "${CLF_VERSION}" "check-circleci-config.sh"
download_script "${CLF_VERSION}" "generate-circleci-config.py"

exit 0
