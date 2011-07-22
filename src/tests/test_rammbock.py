from rammbock import Rammbock
import struct
import unittest
import sys
rammbock = Rammbock()

class TestNumberFormatting(unittest.TestCase):

    def setUp(self):
        rammbock._data = ""
        rammbock._binary = ""

    def _unpack_bytes_to_hex_string(self):
        temp = ""
        for a in rammbock._data:
            temp += hex(struct.unpack('B', a)[0])[2:].rjust(2, '0')
        return temp

    def test_add_even_amount_of_numbers_as_tbcd(self):
        rammbock.add_number_as_tbcd('358', '6100000000001')
        temp = self._unpack_bytes_to_hex_string()
        print temp
        assert temp == '5368010000000010'

    def test_add_odd_amount_of_numbers_as_tbcd(self):
        rammbock.add_number_as_tbcd('358', '6100')
        temp = self._unpack_bytes_to_hex_string()
        print temp
        assert temp == '536801f0'

    def test_add_long_number(self):
        long_int = '2133242342342342135324543'
        rammbock.add_number_as_tbcd(str(long_int))
        temp = self._unpack_bytes_to_hex_string()
        assert temp == '123342322443322431354245f3'
