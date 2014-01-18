#!/usr/bin/env bash -xv

if [ $# != 0 ]; then
    echo "usage: `basename $0`"
    exit 1
fi

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

if [ "$PWD" != "$SCRIPT_DIR_NAME" ]; then
    cd $SCRIPT_DIR_NAME
fi

ARTIFACTS_DIR_NAME=$SCRIPT_DIR_NAME/artifacts
rm -rf $ARTIFACTS_DIR_NAME/* >& /dev/null
mkdir $ARTIFACTS_DIR_NAME

pushd ../..
rm -rf build >& /dev/null
rm -rf clf.egg-info >& /dev/null
rm -rf dist >& /dev/null
python setup.py sdist
popd
cp ../../dist/clf-*.*.tar.gz $ARTIFACTS_DIR_NAME/.
cp ~/.boto $ARTIFACTS_DIR_NAME/.

# vagrant up
