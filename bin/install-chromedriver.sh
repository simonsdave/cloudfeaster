#!/usr/bin/env bash

set -e

if [ $# != 0 ]; then
    echo "usage: $(basename "$0")" >&2
    exit 1
fi

# based on info in http://chromedriver.chromium.org/downloads
# choose the chromedriver version based on the chrome version

if [[ "$(which google-chrome || true)" != "" ]]; then
    # "google-chrome --version" returns something like "Google Chrome 87.0.4280.141"
    BROWSER_VERSION=$(google-chrome --version)
    BROWSER_MAJOR_VERSION_NUMBER=$(echo "${BROWSER_VERSION}" | sed -e 's|^Google Chrome ||g' | sed -e 's|\..*$||g')
elif [[ "$(which chromium-browser)" != "" ]]; then
    # "chromium-browser --version" returns something like "Chromium 87.0.4280.66 Built on Ubuntu , running on Ubuntu 18.04"
    BROWSER_VERSION=$(chromium-browser --version)
    BROWSER_MAJOR_VERSION_NUMBER=$(echo "${BROWSER_VERSION}" | sed -e 's|^[^0-9]*||g' | sed -e 's|\..*$||g')
else
    echo "Could not find chrome or chromium so chromedriver not installed." >&2
    exit 1
fi

case "${BROWSER_MAJOR_VERSION_NUMBER}" in

  85)
    CHROMEDRIVER_VERSION=85.0.4183.87
    ;;

  86)
    CHROMEDRIVER_VERSION=86.0.4240.22
    ;;

  87)
    CHROMEDRIVER_VERSION=87.0.4280.20
    ;;

  *)
    echo "Don't know what to do with browser version >>>${BROWSER_VERSION}<<<" >&2
    exit 1
    ;;
esac

echo "Version >>>${CHROMEDRIVER_VERSION}<<< of ChromeDriver being installed"

apt-get install -y unzip
curl -s --output chromedriver.zip "http://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip chromedriver.zip
rm chromedriver.zip
mv chromedriver /usr/bin/.
chown root.root /usr/bin/chromedriver
chmod a+wrx /usr/bin/chromedriver

exit 0
