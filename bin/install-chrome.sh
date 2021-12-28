#!/usr/bin/env sh

set -e

usage() {
    echo "usage: $(basename "$0") [--chrome|--chromium]" >&2
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
            curl -s https://dl-ssl.google.com/linux/linux_signing_key.pub | APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=DoNotWarn apt-key add -
            sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
            apt-get update -y
            apt-get install -y google-chrome-stable
            ;;
        *)
            echo "Can only install Chrome on Ubuntu not >>>${OS}<<<" >&2
            exit 1
            ;;
    esac
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
fi

exit 0
