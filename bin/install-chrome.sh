#!/usr/bin/env sh

set -e

usage() {
    echo "usage: $(basename "$0") [--chrome|--chromium]" >&2
}

chrome_version() {
    if google-chrome --version > /dev/null 2>&1; then
        # "google-chrome --version" returns something like "Google Chrome 87.0.4280.141"
        google-chrome --version | sed -e 's|^[^0-9]*||g' | sed -e 's|[^0-9]*$||g'
    fi
}

chromium_version() {
    if chromium-browser --version > /dev/null 2>&1; then
        # "chromium-browser --version" returns something like
        #   "Chromium 87.0.4280.66 Built on Ubuntu , running on Ubuntu 18.04"
        # or
        #   "Chromium 93.0.4577.82 "
        chromium-browser --version | sed -e 's|^[^0-9]*||g' | sed -e 's|Built.*$||g' | sed -e 's|\s*$||'
    fi
}

validate_browser_version() {
    BROWSER=${1:-}
    BROWSER_VERSION=${2:-}
    OS=${3:-}

    if [ "${BROWSER_VERSION}" = "" ]; then
        echo "Failed to install >>>${BROWSER}<<< on >>>${OS}<<<." >&2
        exit 1
    fi

    echo "Installed >>>${BROWSER}<<< version >>>${BROWSER_VERSION}<<< on >>>${OS}<<<"
}

CHROME=0
CHROMIUM=0
VERSION=0

while true
do
    case "$(echo "${1:-}" | tr "[:upper:]" "[:lower:]")" in
        --chrome)
            shift
            CHROME=1
            ;;
        --chromium)
            shift
            CHROMIUM=1
            ;;
        --version)
            shift
            VERSION=1
            ;;
        --help)
            shift
            usage
            exit 0
            ;;
        *)
            break
            ;;
    esac
done

if [ $# -ne 0 ]; then
    usage
    exit 1
fi

if [ ${CHROME} -eq 0 ] && [ ${CHROMIUM} -eq 0 ]; then
    echo "must specify at least one of either --chrome or --chromium command line options" >&2
    exit 1
fi

if [ ${VERSION} -eq 1 ]; then
    if [ ${CHROME} -eq 1 ]; then
        chrome_version
    fi
    if [ ${CHROMIUM} -eq 1 ]; then
        chromium_version
    fi
    exit 0
fi

if which apk > /dev/null 2>&1; then
    OS=Alpine
elif which apt-get > /dev/null 2>&1; then
    OS=Ubuntu
else
    echo "Only Ubuntu and Alpine are supported" >&2
    exit 1
fi

if [ ${CHROME} -eq 1 ]; then
    echo "Installing Google Chrome"

    case "${OS}" in
        Ubuntu)
            apt-get update -y

            curl -o /tmp/google-chrome-stable_current_amd64.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
            apt-get install -y /tmp/google-chrome-stable_current_amd64.deb
            ;;
        *)
            echo "Can only install Chrome on Ubuntu not >>>${OS}<<<" >&2
            exit 1
            ;;
    esac

    validate_browser_version "Chrome" "$(chrome_version)" "${OS}"
fi

if [ ${CHROMIUM} -eq 1 ]; then
    echo "Installing Chromium"

    case "${OS}" in
        Ubuntu)
            apt-get update -y
            apt-get install -y chromium-browser
            ;;
        Alpine)
            apk add chromium
            ;;
        *)
            echo "Can only install Chromium on Ubuntu and Alpine not >>>${OS}<<<" >&2
            exit 1
            ;;
    esac

    validate_browser_version "Chromium" "$(chromium_version)" "${OS}"
fi

exit 0
