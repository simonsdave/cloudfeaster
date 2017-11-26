#!/usr/bin/env bash

#
# increment the project's version number
#

set -e

if [ $# != 0 ]; then
    echo "usage: $(basename "$0")" >&2
    exit 1
fi

REPO_ROOT_DIR=$(git rev-parse --show-toplevel)
REPO=$(basename "$REPO_ROOT_DIR")
INIT_DOT_PY=$REPO_ROOT_DIR/${REPO//-/_}/__init__.py
CURRENT_VERSION=$(grep __version__ "$INIT_DOT_PY" | sed -e "s|^.*=\\s*['\"]||g" | sed -e "s|['\"].*$||g")

# the pip install below is necessary make it super simple
# to figure out the project's next version
pip install semantic-version > /dev/null

NEXT_VERSION=$(python -c "import semantic_version; print semantic_version.Version('$CURRENT_VERSION').next_minor()")

sed -i -e "s|^\\s*__version__\\s*=\\s*['\"]$CURRENT_VERSION['\"]\\s*$|__version__ = '$NEXT_VERSION'|g" "$INIT_DOT_PY"

exit 0
