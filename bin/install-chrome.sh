#!/usr/bin/env bash

set -e

if [ $# != 0 ]; then
    echo "usage: $(basename "$0")" >&2
    exit 1
fi

curl -s https://dl-ssl.google.com/linux/linux_signing_key.pub | APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=DoNotWarn apt-key add -
sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
apt-get update -y
apt-get install -y google-chrome-stable

exit 0
