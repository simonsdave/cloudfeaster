#!/usr/bin/env bash

set -e

if [ $# != 1 ]; then
    echo "usage: $(basename "$0") <chromedriver-version>" >&2
    exit 1
fi

CHROMEDRIVER_VERSION=${1:-}

apt-get install -y unzip
curl -s --output chromedriver.zip "http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
unzip chromedriver.zip
rm chromedriver.zip
mv chromedriver /usr/bin/.
chown root.root /usr/bin/chromedriver
chmod a+wrx /usr/bin/chromedriver

exit 0
