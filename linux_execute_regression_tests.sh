#!/bin/bash
base=`dirname $0`
default_target=
if [ -z "$*" ]
    then
      default_target=atests
fi
pybot -c regression -L debug --variablefile "$base/linux_vars.py" --pythonpath "$base/src/" $default_target "$@"
