import unittest
from Message import _MessageStruct, Field
from binary_conversions import to_bin


class TestMessages(unittest.TestCase):

    def test_in(self):
        msg = _MessageStruct('foo')
        msg['a'] = 1
        msg['b'] = 1
        msg['c'] = 1
        self.assertTrue('a' in msg)
        self.assertFalse('d' in msg)

class TestFields(unittest.TestCase):

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
        

if __name__ == "__main__":
    unittest.main()