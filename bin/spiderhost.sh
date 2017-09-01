#!/usr/bin/env bash

# Execute this script to run a spider inside a docker container.
#
# This script is a wrapper around spiderhost.py that simply makes
# sure Xvfb is running before spiderhost.py executes is this script
# is being run on a linux OS.

if [ "$#" == 0 ]; then
    echo "usage: $(basename "$0") <spider> <arg1> ... <argN>" >&2
    exit 1
fi

if [ "Linux" == "$(uname -s)" ]; then
    if [ "" == "$DISPLAY" ]; then
        export DISPLAY=:99
    fi
    # Xvfb will just fail to start of Xvfb is already running
    Xvfb $DISPLAY -ac -screen 0 1280x1024x24 >& /dev/null &
fi

if ! spiderhost.py "${@}"; then
    exit 2
fi

exit 0
