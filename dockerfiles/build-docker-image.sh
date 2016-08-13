#!/usr/bin/env bash
#
# This script builds Cloudfeaster's cloudfeaster docker image
#

set -e

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

VERBOSE=0
TAG="latest"

while true
do
    OPTION=`echo ${1:-} | awk '{print tolower($0)}'`
    case "$OPTION" in
        -v)
            shift
            VERBOSE=1
            ;;
        -t)
            shift
            # this script can be called by travis which may pass
            # a zero length tag argument and hence the need for
            # the if statement below
            if [ "${1:-}" != "" ]; then
                TAG="${1:-}"
            fi
            # the shift assumes the arg after the -t is always a
            # tag name it just might be a zero length tag name
            shift
            ;;
        *)
            break
            ;;
    esac
done

if [ $# != 2 ] && [ $# != 3 ]; then
    echo "usage: `basename $0` [-v] [-t <tag>] <cloudfeaster-tar-gz> <username> [<password>]" >&2
    exit 1
fi

CLOUDFEASTER_TAR_GZ=${1:-}
USERNAME=${2:-}
PASSWORD=${3:-}

IMAGENAME=$USERNAME/cloudfeaster:$TAG

cp "$CLOUDFEASTER_TAR_GZ" "$SCRIPT_DIR_NAME/cloudfeaster.tar.gz"
docker build -t $IMAGENAME "$SCRIPT_DIR_NAME"
rm "$SCRIPT_DIR_NAME/cloudfeaster.tar.gz"

if [ "$PASSWORD" != "" ]; then
    docker login --username="$USERNAME" --password="$PASSWORD"
    docker push $IMAGENAME
fi

exit 0
