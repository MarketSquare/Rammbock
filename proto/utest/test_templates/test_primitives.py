import unittest

from templates.primitives import Length, Char, UInt, PDU
from Message import Struct, Field
from binary_tools import to_bin


class TestTemplateFields(unittest.TestCase):

    def test_uint_static_field(self):
        field = UInt(5, "field", 8)
        self.assertTrue(field.length.static)
        self.assertEquals(field.name, "field")
        self.assertEquals(field.default_value, '8')
        self.assertEquals(field.type, 'uint')
        self.assertEquals(field.encode({}, {}, None).hex, '0x0000000008')

    def test_char_static_field(self):
        field = Char(5, "char_field", 'foo')
        self.assertTrue(field.length.static)
        self.assertEquals(field.name, "char_field")
        self.assertEquals(field.default_value, 'foo')
        self.assertEquals(field.type, 'char')
        self.assertEquals(field.encode({}, {}, None)._raw, 'foo\x00\x00')
        self.assertEquals(field.encode({}, {}, None).bytes, 'foo\x00\x00')

    def test_encoding_missing_value_fails(self):
        field = UInt(2, 'foo', None)
        self.assertRaises(Exception, field.encode, {}, {})
        field = UInt(2, 'foo', '')
        self.assertRaises(Exception, field.encode, {}, {})

    def test_encoding_illegal_value_fails(self):
        field = UInt(2, 'foo',  '(1|2)')
        self.assertRaises(Exception, field.encode, {}, {})
        field = UInt(2, 'foo',  'poplpdsf')
        self.assertRaises(Exception, field.encode, {}, {})

    def test_pdu_field_without_subtractor(self):
        field = PDU('value')
        self.assertEquals(field.length.field, 'value')
        self.assertEquals(field.length.subtractor, 0)
        self.assertEquals(field.type, 'pdu')

    def test_pdu_field_with_subtractor(self):
        field = PDU('value-8')
        self.assertEquals(field.length.field, 'value')
        self.assertEquals(field.length.subtractor, 8)

    def test_decode_uint(self):
        field_template = UInt(2, 'field', 6)
        decoded = field_template.decode(to_bin('0xcafe'), {})
        self.assertEquals(decoded.hex, '0xcafe')

    def test_decode_chars(self):
        field_template = Char(2, 'field', 6)
        decoded = field_template.decode(to_bin('0xcafe'), {})
        self.assertEquals(decoded.hex, '0xcafe')

    def test_decode_returns_used_length(self):
        field_template = UInt(2, 'field', 6)
        data = to_bin('0xcafebabeff00ff00')
        decoded = field_template.decode(data, {})
        self.assertEquals(decoded.hex, '0xcafe')
        self.assertEquals(len(decoded), 2)


class TestLittleEndian(unittest.TestCase):

    def test_little_endian_uint_decode(self):
        template = UInt(2, 'field', None)
        field = template.decode(to_bin('0x0100'), None, little_endian=True)
        self.assertEquals(field._raw, to_bin('0x0100'))
        self.assertEquals(field.int, 1)
        self.assertEquals(field.bytes, to_bin('0x0001'))

    def test_little_endian_char_decode(self):
        template = Char(5, 'field', None)
        field = template.decode('hello', None, little_endian=True)
        self.assertEquals(field._raw, 'hello')
        self.assertEquals(field.bytes, 'hello')
        self.assertEquals(field.ascii, 'hello')

    def test_little_endian_uint_encode(self):
        template = UInt(2, 'field', 1)
        field = template.encode({}, {}, None, little_endian=True)
        self.assertEquals(field._raw, to_bin('0x0100'))
        self.assertEquals(field.int, 1)
        self.assertEquals(field.bytes, to_bin('0x0001'))


class TestTemplateFieldValidation(unittest.TestCase):

    def test_validate_uint(self):
        template = UInt(2, 'field', 4)
        field = Field('uint', 'field', to_bin('0x0004'))
        self._should_pass(template.validate({'field':field}, {}))

    def _should_pass(self, validation):
        self.assertEquals(validation, [])

    def _should_fail(self, validation, number_of_errors):
        self.assertEquals(len(validation), number_of_errors)

    def test_fail_validating_uint(self):
        template = UInt(2, 'field', 4)
        field = Field('uint', 'field', to_bin('0x0004'))
        self._should_fail(template.validate({'field':field}, {'field':'42'}), 1)


class TestLength(unittest.TestCase):

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
        self.assertRaises(Exception,Length,'length-messageId')

    def test_dynamic_length_with_subtractor(self):
        length = Length('length-8')
        self.assertEquals(length.calc_value(18), 10)
        self.assertEquals(length.solve_parameter(10), 18)

    def test_dynamic_length(self):
        length = Length('length')
        self.assertEquals(length.calc_value(18), 18)
        self.assertEquals(length.solve_parameter(18), 18)

    def test_get_field_name(self):
        length = Length('length-8')
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
        self._assert_alignment('5','4',8)
        self._assert_alignment('5','1',5)
        self._assert_alignment('3','4',4)
        self._assert_alignment('1','4',4)
        self._assert_alignment('25','4',28)
        self._assert_alignment('25','',25)
        self._assert_alignment('25',None,25)

    def _assert_alignment(self, length, alignment, result):
        self.assertEquals(Length(length, alignment).decode_lengths(None)[1], result)

    def test_align_must_be_int(self):
        self.assertRaises(Exception, Length, 'foo', 'len')
        self.assertRaises(Exception, Length, '5', '0')
        self.assertRaises(Exception, Length, 'foo-1', '-1')


class TestAlignment(unittest.TestCase):

    def test_encode_aligned_uint(self):
        uint = UInt(1,'foo', '0xff', align='4')
        encoded = uint.encode({}, {}, None)
        self.assertEquals(encoded.int, 255)
        self.assertEquals(encoded.hex, '0xff')
        self.assertEquals(len(encoded), 4)
        self.assertEquals(encoded._raw, to_bin('0xff00 0000'))

    def test_decode_aligned_uint(self):
        uint = UInt(1,'foo', None, align='4')
        decoded = uint.decode(to_bin('0xff00 0000'), None)
        self.assertEquals(decoded.int, 255)
        self.assertEquals(decoded.hex, '0xff')
        self.assertEquals(len(decoded), 4)
        self.assertEquals(decoded._raw, to_bin('0xff00 0000'))

    #TODO: more combinations, handling chars

if __name__ == '__main__':
    unittest.main()
