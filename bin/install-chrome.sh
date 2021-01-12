#!/usr/bin/env sh

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

if [ $# -ne 0 ]; then
    usage
    exit 1
fi

if [ ${CHROME} -eq 0 ] && [ ${CHROMIUM} -eq 0 ]; then
    echo "must specify at least one of either --chrome or --chromium command line options" >&2
    exit 1
fi

if [ ${CHROME} -eq 1 ]; then
    echo "Installing Google Chrome"
    curl -s https://dl-ssl.google.com/linux/linux_signing_key.pub | APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=DoNotWarn apt-key add -
    sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
    apt-get update -y
    apt-get install -y google-chrome-stable
fi

if [ ${CHROMIUM} -eq 1 ]; then
    echo "Installing Chromium"
    apt-get update -y
    apt-get install -y chromium-browser
fi

exit 0
