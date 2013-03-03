#!/bin/bash

export BASEDIR=$(cd $(dirname $0); pwd)
export PYTHONPATH=$BASEDIR

exec python $BASEDIR/eyefilinuxui/gui/newui.py $*
