#!/usr/bin/env python

"""Script to run Rammbock unit tests.

Usage:  [interpreter] utest/run.py

Executes unit tests with the selected Python interpreter or with the system
default Python. Takes no options or arguments and just prints this help text
if any is given.

Examples:

    utest/run.py                        # Run tests using system default Python
    python3 utest/run.py                # Run tests using specified Python
    utest/run.py --help                 # Show this help

It is possible to run unit tests files also separately or by using pytest or
nose as the test runner. That allows also running individual tests if needed.
"""

import sys
from os.path import abspath, dirname, join
from unittest import defaultTestLoader, TextTestRunner


ROOT = dirname(dirname(abspath(__file__)))


def run_utests():
    if len(sys.argv) > 1:
        print(__doc__)
        return 251
    suite = defaultTestLoader.discover(join(ROOT, 'utest'), 'test_*.py')
    result = TextTestRunner().run(suite)
    return min(len(result.failures) + len(result.errors), 250)


if __name__ == '__main__':
    sys.path.insert(0, join(ROOT, 'src'))
    rc = run_utests()
    sys.exit(rc)
