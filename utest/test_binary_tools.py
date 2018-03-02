from unittest import TestCase, main
from Rammbock.binary_tools import to_bin, to_bin_of_length, to_hex, to_0xhex, \
    to_binary_string_of_length, to_tbcd_value, to_bin_str_from_int_string, \
    to_tbcd_binary, to_twos_comp, from_twos_comp


class TestBinaryConversions(TestCase):

    def test_empty_values_to_bin(self):
        self.assertEquals(b'', to_bin(None))
        self.assertEquals(b'', to_bin(''))

    def test_integer_to_bin(self):
        self.assertEquals(to_bin(0), b'\x00')
        self.assertEquals(to_bin(5), b'\x05')
        self.assertEquals(to_bin(255), b'\xff')
        self.assertEquals(to_bin(256), b'\x01\x00')
        self.assertEquals(to_bin(18446744073709551615), b'\xff\xff\xff\xff\xff\xff\xff\xff')

    def test_string_integer_to_bin(self):
        self.assertEquals(to_bin('0'), b'\x00')
        self.assertEquals(to_bin('5'), b'\x05')
        self.assertEquals(to_bin('255'), b'\xff')
        self.assertEquals(to_bin('256'), b'\x01\x00')
        self.assertEquals(to_bin('18446744073709551615'), b'\xff\xff\xff\xff\xff\xff\xff\xff')

    def test_binary_to_bin(self):
        self.assertEquals(to_bin('0b0'), b'\x00')
        self.assertEquals(to_bin('0b1'), b'\x01')
        self.assertEquals(to_bin('0b1111 1111'), b'\xff')
        self.assertEquals(to_bin('0b1 0000 0000'), b'\x01\x00')
        self.assertEquals(to_bin('0b01 0b01 0b01'), b'\x15')
        self.assertEquals(to_bin('0b11' * 32), b'\xff\xff\xff\xff\xff\xff\xff\xff')
        self.assertEquals(to_bin('0b11' * 1024), b'\xff\xff\xff\xff\xff\xff\xff\xff' * 32)

    def test_hex_to_bin(self):
        self.assertEquals(to_bin('0x0'), b'\x00')
        self.assertEquals(to_bin('0x00'), b'\x00')
        self.assertEquals(to_bin('0x5'), b'\x05')
        self.assertEquals(to_bin('0xff'), b'\xff')
        self.assertEquals(to_bin('0x100'), b'\x01\x00')
        self.assertEquals(to_bin('0x01 0x02 0x03'), b'\x01\x02\x03')

    def test_integer_larger_than_8_bytes_works(self):
        self.assertEquals(to_bin('18446744073709551616'), b'\x01\x00\x00\x00\x00\x00\x00\x00\x00')

    def test_hex_larger_than_8_bytes_works(self):
        self.assertEquals(to_bin('0xcafebabe f00dd00d deadbeef'), b'\xca\xfe\xba\xbe\xf0\x0d\xd0\x0d\xde\xad\xbe\xef')

    def test_to_bin_of_length(self):
        self.assertEquals(to_bin_of_length(1, 0), b'\x00')
        self.assertEquals(to_bin_of_length(2, 0), b'\x00\x00')
        self.assertEquals(to_bin_of_length(3, 256), b'\x00\x01\x00')
        self.assertRaises(AssertionError, to_bin_of_length, 1, 256)

    def test_to_hex(self):
        self.assertEquals(to_hex(b'\x00'), b'00')
        self.assertEquals(to_hex(b'\x00\x00'), b'0000')
        self.assertEquals(to_hex(b'\x00\xff\x00'), b'00ff00')
        self.assertEquals(to_hex(b'\xca\xfe\xba\xbe\xf0\x0d\xd0\x0d\xde\xad\xbe\xef'), b'cafebabef00dd00ddeadbeef')

    def test_to_0xhex(self):
        self.assertEquals(to_0xhex(b'\x00'), b'0x00')
        self.assertEquals(to_0xhex(b'\xca\xfe\xba\xbe\xf0\x0d\xd0\x0d\xde\xad\xbe\xef'), b'0xcafebabef00dd00ddeadbeef')

    def test_to_0bbinary(self):
        self.assertEquals(to_binary_string_of_length(1, b'\x00'), '0b0')
        self.assertEquals(to_binary_string_of_length(3, b'\x00'), '0b000')
        self.assertEquals(to_binary_string_of_length(9, b'\x01\xff'), '0b111111111')
        self.assertEquals(to_binary_string_of_length(12, b'\x01\xff'), '0b000111111111')
        self.assertEquals(to_binary_string_of_length(68, b'\x01\x00\x00\x00\x00\x00\x00\x00\x00'), '0b0001' + ('0000' * 16))
        self.assertEquals(to_binary_string_of_length(2048, b'\xff\xff\xff\xff\xff\xff\xff\xff' * 32), '0b' + ('11' * 1024))

    def test_to_tbcd_value(self):
        self.assertEquals('1', to_tbcd_value(to_bin('0b11110001')))
        self.assertEquals('11', to_tbcd_value(to_bin('0b00010001')))
        self.assertEquals('2', to_tbcd_value(to_bin('0b11110010')))
        self.assertEquals('23', to_tbcd_value(to_bin('0b00110010')))
        self.assertEquals('123', to_tbcd_value(to_bin('0b0010000111110011')))

    def test_to_tbcd_binary(self):
        self.assertEquals(to_bin('0b11110001'), to_tbcd_binary('1'))
        self.assertEquals(to_bin('0b00010001'), to_tbcd_binary('11'))
        self.assertEquals(to_bin('0b11110010'), to_tbcd_binary('2'))
        self.assertEquals(to_bin('0b00110010'), to_tbcd_binary('23'))
        self.assertEquals(to_bin('0b0010000111110011'), to_tbcd_binary('123'))
        self.assertEquals(to_bin('0b0110001000010010000000100000000000000000000000000000000011110001'), to_tbcd_binary('262120000000001'))

    def test_to_bin_str_from_int_string(self):
        self.assertEquals('00000001', to_bin_str_from_int_string(8, '1'))
        self.assertEquals('00000010', to_bin_str_from_int_string(8, '2'))
        self.assertEquals('0001', to_bin_str_from_int_string(4, '1'))
        self.assertEquals('0010', to_bin_str_from_int_string(4, '2'))
        self.assertEquals('1111', to_bin_str_from_int_string(4, '15'))

    def test_to_twos_comp(self):
        self.assertEquals(184, to_twos_comp("-72", 8))
        self.assertEquals(47, to_twos_comp("47", 8))
        self.assertEquals(147, to_twos_comp("-109", 8))
        self.assertEquals(189, to_twos_comp("-67", 8))
        self.assertEquals(81, to_twos_comp("81", 8))

    def test_from_twos_comp(self):
        self.assertEquals(-72, from_twos_comp(184, 8))
        self.assertEquals(47, from_twos_comp(47, 8))
        self.assertEquals(-109, from_twos_comp(147, 8))
        self.assertEquals(-67, from_twos_comp(189, 8))
        self.assertEquals(81, from_twos_comp(81, 8))
        self.assertEquals(-21, from_twos_comp(65515, 16))
        self.assertEquals(-46, from_twos_comp(65490, 16))

if __name__ == "__main__":
    main()
