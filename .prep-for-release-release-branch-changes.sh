#!/usr/bin/env bash

set -e

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

if [ $# != 1 ]; then
    echo "usage: $(basename "$0") <release-branch>" >&2
    exit 1
fi

RELEASE_BRANCH=${1:-}

sed -i '' \
    -e \
    "s|/tree/master|/tree/$RELEASE_BRANCH|g" \
    "$SCRIPT_DIR_NAME/README.md"

sed -i '' \
    -e \
    "s|(docs|(https://github.com/simonsdave/cloudfeaster/tree/$RELEASE_BRANCH/docs|g" \
    "$SCRIPT_DIR_NAME/README.md"

rm -f "$SCRIPT_DIR_NAME/README.rst"
pandoc "$SCRIPT_DIR_NAME/README.md" -o "$SCRIPT_DIR_NAME/README.rst"

rm -rf "$SCRIPT_DIR_NAME/dist"
python "$SCRIPT_DIR_NAME/setup.py" bdist_wheel sdist --formats=gztar

exit 0
