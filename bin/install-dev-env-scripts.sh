#!/usr/bin/env bash

#
# should be run out of the spider repo - typically expect cfg4dev
# master will maintain reasonble backward compatibility
#
# curl -s -L https://raw.githubusercontent.com/simonsdave/cloudfeaster/master/install.sh | bash -s --
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

DEV_ENV_VERSION=$(curl -s -L "https://raw.githubusercontent.com/simonsdave/cloudfeaster/v${CLF_VERSION}/dev_env/dev-env-version.txt")

pip install "git+https://github.com/simonsdave/dev-env.git@$DEV_ENV_VERSION"

download_script "${CLF_VERSION}" "run-all-spiders.sh"
download_script "${CLF_VERSION}" "run-spider.sh"
download_script "${CLF_VERSION}" "check-consistent-clf-version.sh"

exit 0
