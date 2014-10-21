#!/bin/bash
base=`dirname $0`
export PATH=$PATH:/usr/local/bin
default_target=
if [ -z "$*" ]
    then
      default_target="$base/atest"
fi
pybot -c regression --exclude background -L debug --pythonpath "$base/src/" $default_target "$@"
