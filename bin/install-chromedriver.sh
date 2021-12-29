#!/usr/bin/env sh

set -e

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

usage() {
    echo "usage: $(basename "$0")" >&2
}

while true
do
    case "$(echo "${1:-}" | tr "[:upper:]" "[:lower:]")" in
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

if [ $# != 0 ]; then
    usage
    exit 1
fi

if ! which curl > /dev/null 2>&1; then
    echo "Doesn't look like cURL is installed." >&2
    exit 1
fi

if ! which unzip > /dev/null 2>&1; then
    echo "Doesn't look like unzip is installed." >&2
    exit 1
fi

BROWSER_VERSION=$("${SCRIPT_DIR_NAME}/install-chrome.sh" --chrome --version)
if [ "${BROWSER_VERSION}" != "" ]; then
    BROWSER=Chrome
else
    BROWSER_VERSION=$("${SCRIPT_DIR_NAME}/install-chrome.sh" --chromium --version)
    if [ "${BROWSER_VERSION}" != "" ]; then
        BROWSER=Chromium
    fi
fi

if [ "${BROWSER}" = "" ] || [ "${BROWSER_VERSION}" = "" ]; then
    echo "Could not find chrome or chromium so chromedriver not installed." >&2
    exit 1
fi

# http://chromedriver.chromium.org/downloads/version-selection describes
# the correct process for determining the right version of chromedriver
# to install
BROWSER_VERSION_MINUS_LAST_NUMBER=$(echo "${BROWSER_VERSION}" | sed -e 's|\.[0-9]*$||')
URL=https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${BROWSER_VERSION_MINUS_LAST_NUMBER}
CHROMEDRIVER_VERSION=$(curl -s "${URL}")

if which apk > /dev/null 2>&1; then

    echo "Installing ChromeDriver via apk for >>>${BROWSER}<<< version >>>${BROWSER_VERSION}<<< - would like ChromeDriver version >>>${BROWSER_VERSION_MINUS_LAST_NUMBER}<<<"

    apk add chromium-chromedriver

else

    echo "Installing ChromeDriver version >>>${CHROMEDRIVER_VERSION}<<< for >>>${BROWSER}<<< version >>>${BROWSER_VERSION}<<<"

    curl -s --output chromedriver.zip "http://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
    unzip chromedriver.zip
    rm chromedriver.zip
    mv chromedriver /usr/bin/.
    chown root.root /usr/bin/chromedriver
    chmod a+wrx /usr/bin/chromedriver

fi

echo "Installed ChromeDriver version >>>$(chromedriver --version)<<<"

exit 0
