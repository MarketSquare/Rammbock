#!/bin/bash
my_dir=$(dirname $BASH_SOURCE)
base=$(dirname $my_dir/../..)
export PATH=$PATH:/usr/local/bin
default_target=
if [ -z "$*" ]
    then
      default_target="$base/proto"
fi
pybot -c regression -L debug --pythonpath "$base/src/" $default_target "$@"
