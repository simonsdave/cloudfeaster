#!/usr/bin/env bash

# Execute this script to run a spider inside a docker container.
#
# This script is a wrapper around spiderhost.py that simply makes
# sure Xvfb is running before spiderhost.py executes is this script
# is being run on a linux OS.

if [ "$#" == 0 ]; then
    echo "usage: `basename $0` <spider> <arg1> ... <argN>" >&2
    exit 1
fi

if [ "Linux" == "$(uname -s)" ]; then
    if [ "" == "$DISPLAY" ]; then
        export DISPLAY=:99
    fi
    if [ "0" == "`ps aux | grep \[X\]vfb | wc -l | sed -e "s/[[:space:]]//g"`" ]; then
        Xvfb $DISPLAY -ac -screen 0 1280x1024x24 >& /dev/null &
    fi
fi

spiderhost.py ${@}
if [ "$?" != "0" ]; then
    exit 2
fi

exit 0
