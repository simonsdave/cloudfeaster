#!/usr/bin/env bash

set -e

usage() {
    echo "usage: $(basename "$0") [--chrome] [--chromium]" >&2
}

CHROME=0
CHROMIUM=0

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

if [[ "${CHROME}" == "0" && "${CHROMIUM}" == "0" ]]; then
    echo "must specify either --chrome or --chromium command line options" >&2
    exit 1
fi

if [[ "${CHROME}" == "1" ]]; then
    echo "Installing Google Chrome"
    curl -s https://dl-ssl.google.com/linux/linux_signing_key.pub | APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=DoNotWarn apt-key add -
    sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
    apt-get update -y
    apt-get install -y google-chrome-stable
fi

if [[ "${CHROMIUM}" == "1" ]]; then
    echo "Installing Chromium"
    apt-get install -y chromium-browser
fi

exit 0
