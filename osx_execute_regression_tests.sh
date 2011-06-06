#!/bin/bash
export PATH=$PATH:/usr/local/bin

python2.5 /Library/Python/2.6/site-packages/robotframework-2.5.7-py2.6.egg/robot/runner.py -c regression -L debug --variablefile osx_vars.py --pythonpath src/ atests
