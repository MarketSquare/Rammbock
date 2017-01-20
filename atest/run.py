#!/usr/bin/env python

"""Script to run Rammbock acceptance tests.

Usage:

    atest/run.py [options] [arguments]

Options and arguments are same as accepted by Robot Framework itself. The only
exception is `--help` which prints this help text. If no options or arguments
are given, run all tests under the `atest` directory.

Examples:

    atest/run.py                        # All tests using system default Python
    python3 atest/run.py                # All tests using specified Python
    atest/run.py --test Receiver        # Use certain options
    atest/run.py atest/ipv6.robot       # Specific file as argument
    atest/run.py -X atest/ipv6.robot    # Options and arguments
"""

from os.path import abspath, dirname, exists, join
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
given_args = sys.argv[1:]
if '--help' in given_args:
    sys.exit(__doc__)
if not given_args or not exists(given_args[-1]):
    given_args.append(join(root, 'atest'))

run_cli(args + given_args)
