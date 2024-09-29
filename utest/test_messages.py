from unittest import TestCase, main
from Rammbock.message import Struct, Field, BinaryContainer, BinaryField
from Rammbock.binary_tools import to_bin


def uint_field(value='0x00'):
    return Field('uint', 'name', to_bin(value))


class TestMessages(TestCase):

    def test_in(self):
        msg = Struct('foo', 'foo_type')
        msg['a'] = uint_field()
        msg['b'] = uint_field()
        msg['c'] = uint_field()
        self.assertTrue('a' in msg)
        self.assertFalse('d' in msg)

    def test_parent_references(self):
        msg = Struct('foo', 'foo_type')
        child = Struct('sub', 'subelement_type')
        child['field'] = uint_field()
        msg['subbi'] = child
        self.assertEquals(msg, child._parent)
        self.assertEquals(msg, child['field']._parent._parent)

    def test_conversions(self):
        field = Field('unit', 'name', to_bin('0x00616200'))
        self.assertEquals(field.int, 0x00616200)
        self.assertEquals(field.hex, '0x00616200')
        self.assertEquals(field.ascii, 'ab')
        self.assertEquals(field.bytes, b'\x00\x61\x62\x00')
        self.assertEquals(field.chars, 'ab')
        self.assertEquals(field.bin, '0b00000000' + '01100001' + '01100010' + '00000000')

    def test_not_iterable(self):
        msg = Struct('foo', 'foo_type')
        msg['a'] = uint_field()
        self.assertRaises(TypeError, iter, msg)
        self.assertRaises(TypeError, iter, msg.a)


class TestBinaryContainer(TestCase):

    def _bin_container(self, little_endian=False):
        cont = BinaryContainer('foo', little_endian=little_endian)
        cont['three'] = BinaryField(3, 'three', to_bin('0b101'))
        cont['six'] = BinaryField(6, 'six', to_bin('0b101010'))
        cont['seven'] = BinaryField(7, 'seven', to_bin('0b0101010'))
        return cont

    def setUp(self):
        self.cont = self._bin_container()

    def test_create_binary_container(self):
        self.assertEquals(self.cont.three.bin, '0b101')
        self.assertEquals(self.cont.six.bin, '0b101010')
        self.assertEquals(self.cont.seven.bin, '0b0101010')

    def test_conversions(self):
        self.assertEquals(self.cont.seven.int, 42)
        self.assertEquals(self.cont.seven.bytes, to_bin(42))
        self.assertEquals(self.cont.seven.ascii, '*')

    def test_get_binary_container_bytes(self):
        self.assertEquals(self.cont._raw, to_bin('0b1011 0101 0010 1010'))

    def test_binary_container_length(self):
        self.assertEquals(len(self.cont), 2)

    def test_little_endian_bin_container(self):
        little = self._bin_container(little_endian=True)
        self.assertEquals(little.three.bin, '0b101')
        self.assertEquals(little.six.bin, '0b101010')
        self.assertEquals(little.seven.bin, '0b0101010')
        self.assertEquals(little._raw, to_bin('0b0010 1010 1011 0101'))

    def test_pretty_print_container(self):
        expected = '''BinaryContainer foo
  three = 0b101 (0x05)
  six = 0b101010 (0x2a)
  seven = 0b0101010 (0x2a)
'''
        self.assertEquals(repr(self._bin_container()), expected)
        self.assertEquals(repr(self._bin_container(little_endian=True)), expected)


class TestFieldAlignment(TestCase):

    def _assert_align(self, value, length, raw):
        field = Field('uint', 'name', to_bin(value), aligned_len=length)
        self.assertEquals(field.int, int(value, 16))
        self.assertEquals(field.hex, value)
        self.assertEquals(field._raw, to_bin(raw))
        self.assertEquals(field.bytes, to_bin(value))
        if length:
            self.assertEquals(len(field), length)

    def test_align_field(self):
        self._assert_align('0xff', 4, '0xff00 0000')
        self._assert_align('0x00ff', 4, '0x00ff 0000')
        self._assert_align('0x00', 4, '0x0000 0000')
        self._assert_align('0xff', None, '0xff')
        self._assert_align('0xff', 6, '0xff00 0000 0000')
        self._assert_align('0x000000ff', 4, '0x0000 00ff')
        self._assert_align('0xff', 1, '0xff')


class TestLittleEndian(TestCase):

    def test_little_endian(self):
        field = Field('uint', 'name', to_bin('0x0100'), little_endian=True)
        self.assertEquals(field._raw, to_bin('0x0100'))
        self.assertEquals(field.int, 1)
        self.assertEquals(field.bytes, to_bin('0x0001'))
        self.assertEquals(field.hex, '0x0001')

    def test_little_endian_with_align(self):
        field = Field('uint', 'name', to_bin('0x0100'), aligned_len=5, little_endian=True)
        self.assertEquals(field._raw, to_bin('0x0100000000'))
        self.assertEquals(field.int, 1)
        self.assertEquals(field.bytes, to_bin('0x0001'))
        self.assertEquals(field.hex, '0x0001')


if __name__ == "__main__":
    main()
