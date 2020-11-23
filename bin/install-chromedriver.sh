#!/usr/bin/env bash

# http://chromedriver.chromium.org/

set -e

if [ $# != 0 ]; then
    echo "usage: $(basename "$0")" >&2
    exit 1
fi

# based on info in http://chromedriver.chromium.org/downloads
# choose the chromedriver version based on the chrome version

GOOGLE_CHROME_VERSION=$(google-chrome --version)
echo "Version >>>${GOOGLE_CHROME_VERSION}<<< of Google Chrome is installed"
case $(echo "${GOOGLE_CHROME_VERSION}" | sed -e 's|^Google Chrome ||g' | sed -e 's|\..*$||g') in

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
    echo "Don't know what to do with version >>>${GOOGLE_CHROME_VERSION}<<< of Google Chrome" >&2
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
