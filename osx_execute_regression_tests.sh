#!/bin/bash
export PATH=$PATH:/usr/local/bin
pybot -c regression -L debug --variablefile osx_vars.py --pythonpath src/ "$@" atests
