#!/bin/bash
base=`dirname $0`
export PATH=$PATH:/usr/local/bin
default_target=
if [ -z "$*" ]
    then
      default_target="$base/atests"
fi
pybot -c regression -L debug --variablefile "$base/config/osx_vars.py" -d "$base/reports/" --pythonpath "$base/src/" $default_target "$@"
