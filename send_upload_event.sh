#!/bin/bash

export BASEDIR=$(cd $(dirname $0); pwd)
export PYTHONPATH=$BASEDIR

exec python $BASEDIR/eyefilinuxui/send_upload_event.py $*
