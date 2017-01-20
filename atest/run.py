#!/usr/bin/env python

from os.path import abspath, dirname, join
import sys

from robot import run_cli


args = [
    '--critical', 'regression',
    '--exclude', 'background',
    '--loglevel', 'debug',
    '--dotted'
]
root = dirname(dirname(abspath(__file__)))
sys.path.insert(0, join(root, 'src'))
given_args = sys.argv[1:] if len(sys.argv) > 1 else [join(root, 'atest')]

run_cli(args + given_args)
