#!/bin/bash
base=`dirname $0`
export PATH=$PATH:/usr/local/bin
pybot -L DEBUG --pythonpath "$base/src/" "$@"
