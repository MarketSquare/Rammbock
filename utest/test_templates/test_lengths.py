from unittest import TestCase, main
from Rammbock.message import Struct, Field
from Rammbock.templates.primitives import Length
from Rammbock.binary_tools import to_bin


class TestLength(TestCase):

    def test_create_length(self):
        length = Length('5')
        self.assertTrue(length.static)

    def test_create_length_dynamic(self):
        length = Length('length')
        self.assertFalse(length.static)

    def test_static_length(self):
        length = Length('5')
        self.assertEquals(length.value, 5)

    def test_only_one_variable_in_dynamic_length(self):
        self.assertRaises(Exception, Length, 'length-messageId')

    def test_dynamic_length_with_subtractor(self):
        length = Length('length-8')
        self.assertEquals(length.calc_value(18), 10)
        self.assertEquals(length.solve_parameter(10), 18)

    def test_dynamic_length_with_addition(self):
        length = Length('length+8')
        self.assertEquals(length.calc_value(10), 18)
        self.assertEquals(length.solve_parameter(18), 10)

    def test_dynamic_length_with_multiplier(self):
        length = Length('length*3')
        self.assertEquals(length.calc_value(4), 12)
        self.assertEquals(length.solve_parameter(12), 4)
        self.assertEquals(length.solve_parameter(13), 5)
        self.assertEquals(length.solve_parameter(14), 5)

    def test_dynamic_length(self):
        length = Length('length')
        self.assertEquals(length.calc_value(18), 18)
        self.assertEquals(length.solve_parameter(18), 18)

    def test_get_field_name(self):
        length = Length('length-8')
        self.assertEquals(length.field, 'length')

    def test_trim_field_names(self):
        length = Length('  length - 8  ')
        self.assertEquals(length.field, 'length')
        length = Length('  length +  8  ')
        self.assertEquals(length.field, 'length')

    def test_decode_dynamic(self):
        msg = Struct('foo', 'foo_type')
        msg['len'] = Field('uint', 'len', to_bin('0x04'))
        dyn_len = Length('len')
        self.assertEquals(dyn_len.decode(msg), 4)

    def test_decode_dynamic_with_subtractor(self):
        msg = Struct('foo', 'foo_type')
        msg['len'] = Field('uint', 'len', to_bin('0x04'))
        dyn_len = Length('len-2')
        self.assertEquals(dyn_len.decode(msg), 2)

    def test_decode_static(self):
        stat_len = Length('5')
        self.assertEquals(stat_len.decode(None), 5)

    def test_align_static(self):
        self._assert_alignment('5', '4', 8)
        self._assert_alignment('5', '1', 5)
        self._assert_alignment('3', '4', 4)
        self._assert_alignment('1', '4', 4)
        self._assert_alignment('25', '4', 28)
        self._assert_alignment('25', '', 25)
        self._assert_alignment('25', None, 25)

    def _assert_alignment(self, length, alignment, result):
        self.assertEquals(Length(length, alignment).decode_lengths(None, None)[1], result)

    def test_align_must_be_int(self):
        self.assertRaises(Exception, Length, 'foo', 'len')
        self.assertRaises(Exception, Length, '5', '0')
        self.assertRaises(Exception, Length, 'foo-1', '-1')


if __name__ == '__main__':
    main()
