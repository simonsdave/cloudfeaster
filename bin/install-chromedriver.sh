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
    BROWSER_VERSION=$( google-chrome --version | sed -e 's|^Google Chrome ||g' | sed -e 's|[^0-9]*$||g' )
elif chromium-browser --version > /dev/null 2>&1; then
    # "chromium-browser --version" returns something like "Chromium 87.0.4280.66 Built on Ubuntu , running on Ubuntu 18.04"
    BROWSER=Chromium
    BROWSER_VERSION=$( chromium-browser --version | sed -e 's|^[^0-9]*||g' | sed -e 's| Built.*$||g' )
else
    echo "Could not find chrome or chromium so chromedriver not installed." >&2
    exit 1
fi

# based on info in http://chromedriver.chromium.org/downloads
# versions are as of 10 Jan '21 @ 12:05 PM EST

case "${BROWSER_VERSION}" in

  85.*)
    CHROMEDRIVER_VERSION=85.0.4183.87
    ;;

  86.*)
    CHROMEDRIVER_VERSION=86.0.4240.22
    ;;

  87.*)
    CHROMEDRIVER_VERSION=87.0.4280.88
    ;;

  88.*)
    CHROMEDRIVER_VERSION=88.0.4324.27
    ;;

  *)
    echo "Don't know what to do with version >>>${BROWSER_VERSION}<<< of browser >>>${BROWSER}<<<" >&2
    exit 1
    ;;
esac

echo "Version >>>${CHROMEDRIVER_VERSION}<<< of ChromeDriver being installed for version >>>${BROWSER_VERSION}<<< of browser >>>${BROWSER}<<<"

curl -s --output chromedriver.zip "http://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip chromedriver.zip
rm chromedriver.zip
mv chromedriver /usr/bin/.
chown root.root /usr/bin/chromedriver
chmod a+wrx /usr/bin/chromedriver

exit 0
