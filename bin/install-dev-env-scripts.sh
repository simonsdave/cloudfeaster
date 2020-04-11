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

    REPO_DOT_SH=$(command -v repo.sh)
    SCRIPT_INSTALL_DIR=$(dirname "$REPO_DOT_SH")

    curl \
       -s \
       -L \
       -o "${SCRIPT_INSTALL_DIR}/${SCRIPT}" \
       "https://raw.githubusercontent.com/simonsdave/cloudfeaster/v${CLF_VERSION}/bin/${SCRIPT}"

    chmod u+x "${SCRIPT_INSTALL_DIR}/${SCRIPT}"

    return 0
}

set -e

if [ $# != 0 ]; then
    echo "usage: $(basename "$0")" >&2
    exit 1
fi

REPO_ROOT_DIR=$(git rev-parse --show-toplevel)

CLF_VERSION=$(grep cloudfeaster== "${REPO_ROOT_DIR}/setup.py" | sed -e "s|^[[:space:]]*['\"]cloudfeaster==||g" | sed -e "s|['\"].*$||g")

DEV_ENV_VERSION=$(curl -s -L "https://raw.githubusercontent.com/simonsdave/cloudfeaster/v${CLF_VERSION}/.circleci/config.yml" | grep 'image:' | tail -1 | sed -e 's|[[:space:]]*$||g' | sed -e 's|^.*dev-env:||g')
if [ "${DEV_ENV_VERSION}" == "latest" ]; then DEV_ENV_VERSION=master; fi
curl -s -L https://raw.githubusercontent.com/simonsdave/dev-env/${DEV_ENV_VERSION}/bin/install-dev-env.sh | bash -s -- --dev-env-version "${DEV_ENV_VERSION:-}"

download_script "${CLF_VERSION}" "run-all-spiders.sh"
download_script "${CLF_VERSION}" "run-spider.sh"
download_script "${CLF_VERSION}" "check-circleci-config.sh"
download_script "${CLF_VERSION}" "generate-circleci-config.py"

exit 0
