#!/usr/bin/env sh

set -e

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

if google-chrome --version > /dev/null 2>&1; then
    # "google-chrome --version" returns something like "Google Chrome 87.0.4280.141"
    BROWSER=Chrome
    BROWSER_VERSION=$( google-chrome --version | sed -e 's|^[^0-9]*||g' | sed -e 's|[^0-9]*$||g' )
elif chromium-browser --version > /dev/null 2>&1; then
    # "chromium-browser --version" returns something like "Chromium 87.0.4280.66 Built on Ubuntu , running on Ubuntu 18.04"
    BROWSER=Chromium
    BROWSER_VERSION=$( chromium-browser --version | sed -e 's|^[^0-9]*||g' | sed -e 's| Built.*$||g' )
else
    echo "Could not find chrome or chromium so chromedriver not installed." >&2
    exit 1
fi

# http://chromedriver.chromium.org/downloads/version-selection describes
# the correct process for determining the right version of chromedriver
# to install
URL=https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$(echo "${BROWSER_VERSION}" | sed -e 's|\.[0-9]*$||')
CHROMEDRIVER_VERSION=$(curl -s "${URL}")

if which apk > /dev/null 2>&1; then

    echo "Installing ChromeDriver via apk for >>>${BROWSER}<<< version >>>${BROWSER_VERSION}<<< - would like ChromeDriver version >>>${CHROMEDRIVER_VERSION}<<<"

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
