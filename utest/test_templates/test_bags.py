from unittest import TestCase
from Rammbock.templates.primitives import BagSize
import sys


class TestBagSize(TestCase):

    def test_free_size(self):
        self._assert_min_max('*', 0, sys.maxsize)

    def test_fixed_size(self):
        self._assert_min_max('1', 1, 1)
        self._assert_min_max('1234567890', 1234567890, 1234567890)

    def test_range(self):
        self._assert_min_max('0-1', 0, 1)
        self._assert_min_max('1-80', 1, 80)
        self._assert_min_max('0 - 1', 0, 1)

    def test_invalid_size(self):
        self._assert_fails('y')
        self._assert_fails('-1')
        self._assert_fails('6-0')
        self._assert_fails('0')
        self._assert_fails('0-0')

    def _assert_fails(self, pattern):
        self.assertRaises(AssertionError, BagSize, pattern)

    def _assert_min_max(self, pattern, min, max):
        s = BagSize(pattern)
        self.assertEquals(s.min, min)
        self.assertEquals(s.max, max)
