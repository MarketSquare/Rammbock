from rammbock import Rammbock
import struct
import unittest
from time import time
rammbock = Rammbock()

class TestNumberFormatting(unittest.TestCase):

    def setUp(self):
        rammbock._data = ""
        rammbock._binary = ""

    def _unpack_bytes_to_hex_string(self):
        return  "".join([hex(struct.unpack('B', a)[0])[2:].rjust(2, '0') for a in rammbock._data])

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

    def test_add_mnc_as_tbcd(self):
        rammbock.add_number_as_tbcd(str(262))
        mcc = self._unpack_bytes_to_hex_string()
        assert mcc == '62f2'

    def test_add_mcc_as_tbcd(self):
        rammbock.add_number_as_tbcd(str(12))
        mnc = self._unpack_bytes_to_hex_string()
        assert mnc == '21'

    def test_add_ip_as_hex(self):
        rammbock.add_ip_as_hex("255.255.255.255")
        mnc = self._unpack_bytes_to_hex_string()
        assert mnc == 'ffffffff'

    def test_add_another_ip_as_hex(self):
        rammbock.add_ip_as_hex("1.1.1.1")
        mnc = self._unpack_bytes_to_hex_string()
        assert mnc == '01010101'

    def test_add_false_ip_as_hex(self):
        self.assertRaises(Exception, rammbock.add_ip_as_hex, "255.255.255.256")

    def test_read_from_data(self):
        rammbock.add_decimal_as_octets(50331665,4)
        a = rammbock.read_from_data(4)
        print a
        assert a == "50331665"

    def test_speed_of_read_from_date(self):
        a = "a" * 10000
        rammbock._data = a
        s = time()
        rammbock.read_from_data(len(a))
        b = time()
        print b-s
        assert b-s < 0.2

