#!/usr/bin/env python

"""Script to run Rammbock acceptance tests.

Usage:  [interpreter] atest/run.py [options] [arguments]

Options and arguments are same as accepted by Robot Framework itself. The only
exception is `--help` which prints this help text. Given options are added
after the default configuration. Executes the whole `atest` directory if no
files or directories are given as arguments.

Examples:

    atest/run.py                        # Run tests using system default Python
    python3 atest/run.py                # Run tests using specified Python
    atest/run.py --test IPv6TCP         # Use certain options
    atest/run.py atest/ipv6.robot       # Specific file as an argument
    atest/run.py -X atest/ipv6.robot    # Use both options and arguments
    atest/run.py --help                 # Show this help
"""

from os.path import abspath, dirname, exists, join
import sys

from robot import run_cli


ROOT = dirname(dirname(abspath(__file__)))
CONFIG = [
    '--critical', 'regression',
    '--exclude', 'background',
    '--loglevel', 'debug',
    '--dotted'
]


def run_atests(args):
    if '--help' in args:
        print(__doc__)
        return 251
    if not args or not exists(args[-1]):
        args.append(join(ROOT, 'atest'))
    try:
        run_cli(CONFIG + args)
    except SystemExit as exit:
        return exit.code


if __name__ == '__main__':
    sys.path.insert(0, join(ROOT, 'src'))
    rc = run_atests(sys.argv[1:])
    sys.exit(rc)
