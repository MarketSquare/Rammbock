#!/bin/bash -x
base=`dirname $0`
export PATH=$PATH:/usr/local/bin
pylint --rcfile=.pylintrc src/ > pylint.txt
pep8 --exclude decorator.py src/ > pep8.txt
true
