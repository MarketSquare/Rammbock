import unittest
from binary_tools import to_bin, to_bin_of_length, to_hex, to_0xhex, to_binary_of_length

class TestBinaryConversions(unittest.TestCase):

    def test_integer_to_bin(self):
        self.assertEquals(to_bin(0), '\x00')
        self.assertEquals(to_bin(5), '\x05')
        self.assertEquals(to_bin(255), '\xff')
        self.assertEquals(to_bin(256), '\x01\x00')
        self.assertEquals(to_bin(18446744073709551615L), '\xff\xff\xff\xff\xff\xff\xff\xff')

    def test_string_integer_to_bin(self):
        self.assertEquals(to_bin('0'), '\x00')
        self.assertEquals(to_bin('5'), '\x05')
        self.assertEquals(to_bin('255'), '\xff')
        self.assertEquals(to_bin('256'), '\x01\x00')
        self.assertEquals(to_bin('18446744073709551615'), '\xff\xff\xff\xff\xff\xff\xff\xff')

    def test_binary_to_bin(self):
        self.assertEquals(to_bin('0b0'), '\x00')
        self.assertEquals(to_bin('0b1'), '\x01')
        self.assertEquals(to_bin('0b1111 1111'), '\xff')
        self.assertEquals(to_bin('0b1 0000 0000'), '\x01\x00')
        self.assertEquals(to_bin('0b01 0b01 0b01'), '\x15')
        self.assertEquals(to_bin('0b11'*32), '\xff\xff\xff\xff\xff\xff\xff\xff')

    def test_hex_to_bin(self):
        self.assertEquals(to_bin('0x0'), '\x00')
        self.assertEquals(to_bin('0x5'), '\x05')
        self.assertEquals(to_bin('0xff'), '\xff')
        self.assertEquals(to_bin('0x100'), '\x01\x00')
        self.assertEquals(to_bin('0x01 0x02 0x03'), '\x01\x02\x03')

    def test_integer_larger_than_8_bytes_fails(self):
        self.assertRaises(AssertionError, to_bin, '18446744073709551616')
        self.assertRaises(AssertionError, to_bin, '0b11'*33)

    def test_hex_larger_than_8_bytes_works(self):
        self.assertEquals(to_bin('0xcafebabe f00dd00d deadbeef'), '\xca\xfe\xba\xbe\xf0\x0d\xd0\x0d\xde\xad\xbe\xef')

    def test_to_bin_of_length(self):
        self.assertEquals(to_bin_of_length(1, 0), '\x00')
        self.assertEquals(to_bin_of_length(2, 0), '\x00\x00')
        self.assertEquals(to_bin_of_length(3, 256), '\x00\x01\x00')
        self.assertRaises(AssertionError, to_bin_of_length, 1, 256)

    def test_to_hex(self):
        self.assertEquals(to_hex('\x00'), '00')
        self.assertEquals(to_hex('\x00\x00'), '0000')
        self.assertEquals(to_hex('\x00\xff\x00'), '00ff00')
        self.assertEquals(to_hex('\xca\xfe\xba\xbe\xf0\x0d\xd0\x0d\xde\xad\xbe\xef'), 'cafebabef00dd00ddeadbeef')

    def test_to_0xhex(self):
        self.assertEquals(to_0xhex('\x00'), '0x00')
        self.assertEquals(to_0xhex('\xca\xfe\xba\xbe\xf0\x0d\xd0\x0d\xde\xad\xbe\xef'), '0xcafebabef00dd00ddeadbeef')

    def test_to_0bbinary(self):
        self.assertEquals(to_binary_of_length(1,'\x00'), '0b0')
        self.assertEquals(to_binary_of_length(3,'\x00'), '0b000')
        self.assertEquals(to_binary_of_length(9,'\x01\xff'), '0b111111111')
        self.assertEquals(to_binary_of_length(12,'\x01\xff'), '0b000111111111')