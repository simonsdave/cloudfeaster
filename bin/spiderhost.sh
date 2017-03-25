#!/usr/bin/env bash

# Execute this script to run a spider inside a docker container.
#
# This script is a wrapper around spiderhost.py that simply makes
# sure Xvfb is running before spiderhost.py executes is this script
# is being run on a linux OS.
#
# credit for all the session recording goes to the article "Recording
# headless selenium tests to mp4 with Xvfb and ffmpeg" @
# http://afterdesign.net/2016/02/07/recording-headless-selenium-tests-to-mp4.html

set -e

if [ "$#" == 0 ]; then
    echo "usage: `basename $0` <spider> <arg1> ... <argN>" >&2
    exit 1
fi

if [ "Linux" == "$(uname -s)" ]; then
    if [ "" == "$DISPLAY" ]; then
        export DISPLAY=:99
    fi
    if [ "0" == "`ps aux | grep \[X\]vfb | wc -l | sed -e "s/[[:space:]]//g"`" ]; then
        Xvfb $DISPLAY -ac -screen 0 1920x1080x24 >& /dev/null &
    fi
fi

set -x

#
# helpful docs to figure this whole encoding thing
#
# -- http://stackoverflow.com/questions/3377300/what-are-all-codecs-supported-by-ffmpeg
# -- https://trac.ffmpeg.org/wiki/Encode/VP9
#
SESSION_NAME=$(python -c 'import uuid; print uuid.uuid4().hex')
RECORDING_FILENAME=/vagrant/$SESSION_NAME.mp4
CODEC=libx264

tmux new-session -d -s $SESSION_NAME "ffmpeg -f x11grab -video_size 1920x1080 -i 127.0.0.1:$(echo $DISPLAY | sed -e 's/://g') -codec:v $CODEC -r 12 \"$RECORDING_FILENAME\""

spiderhost.py ${@}
if [ "$?" != "0" ]; then
    exit 2
fi

tmux send-keys -t $SESSION_NAME q

set +x

exit 0
