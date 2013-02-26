from unittest import TestCase, main
from Rammbock.templates.containers import Protocol, MessageTemplate, StructTemplate, ListTemplate, UnionTemplate, BinaryContainerTemplate, TBCDContainerTemplate, ConditionalTemplate
from Rammbock.templates.primitives import UInt, PDU, Char, Binary, TBCD
from Rammbock.binary_tools import to_bin_of_length, to_bin
from tools import *


class _WithValidation(object):

    def _should_pass(self, validation):
        self.assertEquals(validation, [])

    def _should_fail(self, validation, number_of_errors):
        self.assertEquals(len(validation), number_of_errors)


class TestProtocol(TestCase):

    def setUp(self):
        self._protocol = Protocol('Test')

    def test_header_length(self):
        self._protocol.add(UInt(1, 'name1', None))
        self.assertEquals(self._protocol.header_length(), 1)

    def test_header_length_with_pdu(self):
        self._protocol.add(UInt(1, 'name1', None))
        self._protocol.add(UInt(2, 'name2', 5))
        self._protocol.add(UInt(2, 'length', None))
        self._protocol.add(PDU('length'))
        self.assertEquals(self._protocol.header_length(), 5)

    def test_verify_undefined_length(self):
        self._protocol.add(UInt(1, 'name1', None))
        self._protocol.add(UInt(2, 'name2', 5))
        self.assertRaises(Exception, self._protocol.add, PDU('length'))

    def test_verify_calculated_length(self):
        self._protocol.add(UInt(1, 'name1', 1))
        self._protocol.add(UInt(2, 'length', None))
        self._protocol.add(PDU('length-8'))
        self.assertEquals(self._protocol.header_length(), 3)


class TestMessageTemplate(TestCase):

    def setUp(self):
        self._protocol = Protocol('TestProtocol')
        self._protocol.add(UInt(2, 'msgId', 5))
        self._protocol.add(UInt(2, 'length', None))
        self._protocol.add(PDU('length-4'))
        self.tmp = MessageTemplate('FooRequest', self._protocol, {})
        self.tmp.add(UInt(2, 'field_1', 1))
        self.tmp.add(UInt(2, 'field_2', 2))

    def test_create_template(self):
        self.assertEquals(len(self.tmp._fields), 2)

    def test_encode_template(self):
        msg = self.tmp.encode({}, {})
        self.assertEquals(msg.field_1.int, 1)
        self.assertEquals(msg.field_2.int, 2)

    def test_message_field_type_conversions(self):
        msg = self.tmp.encode({'field_1': 1024}, {})
        self.assertEquals(msg.field_1.int, 1024)
        self.assertEquals(msg.field_1.hex, '0x0400')
        self.assertEquals(msg.field_1.bytes, '\x04\x00')

    def test_encode_template_with_params(self):
        msg = self.tmp.encode({'field_1': 111, 'field_2': 222}, {})
        self.assertEquals(msg.field_1.int, 111)
        self.assertEquals(msg.field_2.int, 222)

    def test_encode_template_header(self):
        msg = self.tmp.encode({}, {})
        self.assertEquals(msg._header.msgId.int, 5)
        self.assertEquals(msg._header.length.int, 8)

    def test_encode_to_bytes(self):
        msg = self.tmp.encode({}, {})
        self.assertEquals(msg._header.msgId.int, 5)
        self.assertEquals(msg._raw, to_bin_of_length(8, '0x0005 0008 0001 0002'))

    # TODO: make the fields aware of their type?
    # so that uint fields are pretty printed to uints
    # bytes fields to hex bytes
    # and character fields to characters..
    def test_pretty_print(self):
        msg = self.tmp.encode({}, {})
        self.assertEquals(msg._header.msgId.int, 5)
        self.assertEquals(str(msg), 'Message FooRequest')
        self.assertEquals(repr(msg),
                          """Message FooRequest
  Header TestProtocol
    msgId = 5 (0x0005)
    length = 8 (0x0008)
  field_1 = 1 (0x0001)
  field_2 = 2 (0x0002)
""")

    def test_unknown_params_cause_exception(self):
        self.assertRaises(AssertionError, self.tmp.encode, {'unknown': 111}, {})

    def test_decode_message(self):
        msg = self.tmp.decode(to_bin('0xcafebabe'))
        self.assertEquals(msg.field_1.hex, '0xcafe')


class TestStructuredTemplate(TestCase):

    def test_access_struct(self):
        self._protocol = Protocol('TestProtocol')
        self._protocol.add(UInt(2, 'msgId', 5))
        self._protocol.add(UInt(2, 'length', None))
        self._protocol.add(PDU('length-4'))
        self.tmp = MessageTemplate('StructuredRequest', self._protocol, {})
        struct = get_pair()
        self.tmp.add(struct)
        msg = self.tmp.encode({}, {})
        self.assertEquals(msg.pair.first.int, 1)

    def test_create_struct(self):
        struct = get_pair()
        self.assertEquals(struct.name, 'pair')

    def test_add_fields_to_struct(self):
        struct = get_pair()
        encoded = struct.encode({}, {})
        self.assertEquals(encoded.first.int, 1)

    def test_add_fields_to_struct_and_override_values(self):
        struct = get_pair()
        encoded = struct.encode({'pair.first': 42}, {})
        self.assertEquals(encoded.first.int, 42)

    def test_yo_dawg_i_heard(self):
        str_str = get_recursive_struct()
        encoded = str_str.encode({}, {})
        self.assertEquals(encoded.pair.first.int, 1)

    def test_get_recursive_names(self):
        pair = get_pair()
        names = pair._get_params_sub_tree({'pair.foo': 0, 'pairnotyourname.ploo': 2, 'pair.goo.doo': 3})
        self.assertEquals(len(names), 2)
        self.assertEquals(names['foo'], 0)
        self.assertEquals(names['goo.doo'], 3)

    def test_set_recursive(self):
        str_str = get_recursive_struct()
        encoded = str_str.encode({'str_str.pair.first': 42}, {})
        self.assertEquals(encoded.pair.first.int, 42)

    def test_decode_several_structs(self):
        str_list = get_struct_list()
        decoded = str_list.decode(to_bin('0xcafebabe d00df00d'), {})
        self.assertEquals(decoded[0].first.hex, '0xcafe')
        self.assertEquals(decoded[1].second.hex, '0xf00d')

    def test_length_of_struct(self):
        pair = get_pair()
        encoded = pair.encode({}, {})
        self.assertEquals(len(encoded), 4)

    def test_decode_struct(self):
        pair = get_pair()
        decoded = pair.decode(to_bin('0xcafebabe'), {})
        self.assertEquals(decoded.first.hex, '0xcafe')
        self.assertEquals(decoded.second.hex, '0xbabe')


class TestDefaultValues(TestCase):

    def test_default_values(self):
        pair = get_empty_pair()
        encoded = pair.encode({'pair.*': '5'})
        self.assertEquals(encoded.first.int, 5)

    def test_sub_default_values(self):
        pairs = get_empty_recursive_struct()
        encoded = pairs.encode({'*': '1', '3pairs.pair2.*': '2', '3pairs.pair3.*': '3'})
        self.assertEquals(encoded.pair1.first.int, 1)
        self.assertEquals(encoded.pair2.first.int, 2)
        self.assertEquals(encoded.pair3.first.int, 3)


class TestDynamicMessageTemplate(TestCase):

    def setUp(self):
        self._protocol = Protocol('TestProtocol')
        self._protocol.add(UInt(2, 'msgId', 5))
        self._protocol.add(UInt(2, 'length', None))
        self._protocol.add(PDU('length-4'))

    def test_non_existing_dynamic_variable(self):
        tmp = MessageTemplate('Dymagic', self._protocol, {})
        self.assertRaises(Exception, tmp.add, Char('not_existing', 'foo', None))

    def test_non_existing_dynamic_list_variable(self):
        tmp = MessageTemplate('Dymagic', self._protocol, {})
        lst = ListTemplate('not_existing', 'foo', parent=None)
        lst.add(UInt(1, 'bar', None))
        self.assertRaises(Exception, tmp.add, lst)

    def test_decode_dynamic_primitive(self):
        tmp = MessageTemplate('Dymagic', self._protocol, {})
        tmp.add(UInt(1, 'len', None))
        tmp.add(Char('len', 'chars', None))
        tmp.add(UInt(1, 'len2', None))
        tmp.add(Char('len2', 'chars2', None))
        decoded = tmp.decode(to_bin('0x 04 6162 6364 02 6566'))
        self.assertEquals(decoded.len.int, 4)
        self.assertEquals(decoded.chars.ascii, 'abcd')
        self.assertEquals(decoded.chars2.ascii, 'ef')

    def test_encode_dynamic_primitive_with_defined_value(self):
        tmp = MessageTemplate('Dymagic', self._protocol, {})
        tmp.add(UInt(4, 'len', '4'))
        tmp.add(Char('len', 'chars', 'abcd'))
        tmp.add(UInt(4, 'len2', None))
        tmp.add(Char('len2', 'chars2', 'ef'))
        encoded = tmp.encode({'len2': '6'}, {})
        self.assertEquals(encoded.chars.ascii, 'abcd')
        self.assertEquals(len(encoded.chars), 4)
        self.assertEquals(encoded.chars2.ascii, 'ef')
        self.assertEquals(len(encoded.chars2), 6)

    def test_encode_dynamic_primitive_automatically(self):
        tmp = MessageTemplate('Dymagic', self._protocol, {})
        tmp.add(UInt(4, 'len', None))
        tmp.add(Char('len', 'chars', 'abcd'))
        encoded = tmp.encode({}, {})
        self.assertEquals(encoded.chars.ascii, 'abcd')
        self.assertEquals(encoded.len.int, 4)

    def test_decode_dynamic_list(self):
        tmp = MessageTemplate('Dymagic', self._protocol, {})
        tmp.add(UInt(2, 'len', None))
        lst = ListTemplate('len', 'foo', parent=None)
        lst.add(UInt(1, 'bar', None))
        tmp.add(lst)
        decoded = tmp.decode(to_bin('0x 00 04 6162 6364'))
        self.assertEquals(decoded.len.int, 4)
        self.assertEquals(decoded.foo[0].hex, '0x61')

    def test_encode_dynamic_list(self):
        tmp = MessageTemplate('Dymagic', self._protocol, {})
        tmp.add(UInt(2, 'len', None))
        lst = ListTemplate('len', 'foo', parent=None)
        lst.add(UInt(1, 'bar', 1))
        tmp.add(lst)
        encoded = tmp.encode({'len': 6}, {})
        self.assertEquals(len(encoded.foo), 6)

    def test_add_field_with_length_reference_to_parent(self):
        tmp = MessageTemplate('Dymagic', self._protocol, {})
        tmp.add(UInt(2, 'len', None))
        str = StructTemplate('FooType', 'foo', tmp)
        str.add(Char('len', "bar"))

    def test_add_field_with_length_reference_missing(self):
        tmp = MessageTemplate('Dymagic', self._protocol, {})
        tmp.add(UInt(2, 'len', None))
        str = StructTemplate('FooType', 'foo', tmp)
        self.assertRaises(AssertionError, str.add, Char('notfound', "bar"))


class TestMessageTemplateValidation(TestCase):

    def setUp(self):
        self._protocol = Protocol('TestProtocol')
        self._protocol.add(UInt(2, 'msgId', 5))
        self._protocol.add(UInt(2, 'length', None))
        self._protocol.add(PDU('length-4'))
        self.tmp = MessageTemplate('FooRequest', self._protocol, {})
        self.tmp.add(UInt(2, 'field_1', '0xcafe'))
        self.tmp.add(UInt(2, 'field_2', '0xbabe'))

    def test_validate_passing_hex(self):
        msg = self.tmp.decode(to_bin('0xcafebabe'))
        errors = self.tmp.validate(msg, {})
        self.assertEquals(errors, [])

    def test_validate_error_default_value(self):
        msg = self.tmp.decode(to_bin('0xcafedead'))
        errors = self.tmp.validate(msg, {})
        self.assertEquals(errors, ['Value of field field_2 does not match 0xdead!=0xbabe'])

    def test_validate_error_override(self):
        msg = self.tmp.decode(to_bin('0xcafebabe'))
        errors = self.tmp.validate(msg, {'field_2': '0xdead'})
        self.assertEquals(errors, ['Value of field field_2 does not match 0xbabe!=0xdead'])

    def test_validate_two_errors(self):
        msg = self.tmp.decode(to_bin('0xbeefbabe'))
        errors = self.tmp.validate(msg, {'field_2': '0xdead'})
        self.assertEquals(len(errors), 2)

    def test_validate_pattern_pass(self):
        msg = self.tmp.decode(to_bin('0xcafe0002'))
        errors = self.tmp.validate(msg, {'field_2': '(0|2)'})
        self.assertEquals(len(errors), 0)

    def test_validate_pattern_failure(self):
        msg = self.tmp.decode(to_bin('0xcafe0002'))
        errors = self.tmp.validate(msg, {'field_2': '(0|3)'})
        self.assertEquals(len(errors), 1)

    def test_validate_passing_int(self):
        msg = self.tmp.decode(to_bin('0xcafe0200'))
        errors = self.tmp.validate(msg, {'field_2': '512'})
        self.assertEquals(errors, [])

    def test_failing_passing_int(self):
        msg = self.tmp.decode(to_bin('0xcafe0200'))
        errors = self.tmp.validate(msg, {'field_2': '513'})
        self.assertEquals(len(errors), 1)


class TestTemplateFieldValidation(TestCase, _WithValidation):

    def test_validate_struct_passes(self):
        template = get_pair()
        field = template.encode({})
        self._should_pass(template.validate({'pair': field}, {'pair.first': '1'}))

    def test_validate_struct_fails(self):
        template = get_pair()
        field = template.encode({})
        self._should_fail(template.validate({'pair': field}, {'pair.first': '42'}), 1)

    def test_validate_list_succeeds(self):
        template = get_list_of_three()
        encoded = template.encode({}, None)
        self._should_pass(template.validate({'topthree': encoded}, {'topthree[1]': '1'}))

    def test_validate_list_fails(self):
        template = get_list_of_three()
        encoded = template.encode({}, None)
        self._should_fail(template.validate({'topthree': encoded}, {'topthree[1]': '42'}), 1)

    def test_validate_list_list(self):
        template = get_list_list()
        encoded = template.encode({}, None)
        self._should_pass(template.validate({'listlist': encoded}, {'listlist[1][1]': '7'}))
        self._should_fail(template.validate({'listlist': encoded}, {'listlist[1][1]': '42'}), 1)

    def test_validate_struct_list(self):
        template = get_struct_list()
        encoded = template.encode({}, None)
        self._should_pass(template.validate({'liststruct': encoded}, {'liststruct[1].first': '1'}))
        self._should_fail(template.validate({'liststruct': encoded}, {'liststruct[1].first': '42'}), 1)

    def test_dynamic_field_validation(self):
        struct = StructTemplate('Foo', 'foo', parent=None)
        struct.add(UInt(2, 'len', None))
        struct.add(Char('len', 'text', None))
        encoded = struct.encode({'foo.len': 6, 'foo.text': 'fobba'})
        self._should_pass(struct.validate({'foo': encoded}, {'foo.text': 'fobba'}))
        self._should_fail(struct.validate({'foo': encoded}, {'foo.text': 'fob'}), 1)


class TestUnions(TestCase, _WithValidation):

    def _check_length(self, length, *fields):
        union = UnionTemplate('Foo', 'foo', parent=None)
        for value in fields:
            union.add(value)
        self.assertEquals(union.get_static_length(), length)

    def test_union_primitive_length(self):
        self._check_length(2, UInt(1, 'a', 1), UInt(2, 'b', 1))
        self._check_length(1, UInt(1, 'a', 1), UInt(1, 'b', 1))
        self._check_length(4, UInt(4, 'a', 4), UInt(1, 'b', 1), UInt(2, 'c', 1))
        self._check_length(16, UInt(1, 'a', 1), Char(16, 'b', 1))
        self._check_length(10, Char(10, 'a', None), Char(10, 'b', None))

    def test_container_union_length(self):
        self._check_length(4, get_pair(), UInt(2, 'b', 1))
        self._check_length(4, UInt(1, 'a', 1), get_recursive_struct())
        self._check_length(6, get_pair(), get_list_of_three())

    def test_fail_on_dynamic_length(self):
        union = UnionTemplate('NotLegal', 'dymagic', parent=None)
        union.add(UInt(2, 'bar', None))
        struct = StructTemplate('Foo', 'foo', parent=None)
        struct.add(UInt(1, 'len', 22))
        struct.add(Char('len', 'dymagic', 'foo'))
        self.assertRaises(Exception, union.add, struct)

    def test_decode_union(self):
        union = self._get_foo_union()
        decoded = union.decode(to_bin('0xcafebabe'))
        self.assertEquals(decoded.small.hex, '0xca')
        self.assertEquals(decoded.medium.hex, '0xcafe')
        self.assertEquals(decoded.large.hex, '0xcafebabe')

    def test_union_length(self):
        union = self._get_foo_union()
        decoded = union.decode(to_bin('0xcafebabe'))
        self.assertEquals(4, len(decoded))

    def test_get_bytes_from_decoded_union(self):
        union = self._get_foo_union()
        decoded = union.decode(to_bin('0xcafebabe'))
        self.assertEquals(decoded._raw, to_bin('0xcafebabe'))

    def _get_foo_union(self):
        union = UnionTemplate('Foo', 'foo', parent=None)
        union.add(UInt(1, 'small', '0xff'))
        union.add(UInt(2, 'medium', '0xf00d'))
        union.add(UInt(4, 'large', None))
        return union

    def test_encode_union(self):
        union = self._get_foo_union()
        encoded = union.encode({'foo': 'medium'}, {})
        self.assertEquals(encoded._raw, to_bin('0xf00d 0000'))

    def test_encode_union_with_param(self):
        union = self._get_foo_union()
        encoded = union.encode({'foo': 'small', 'foo.small': '0xff'}, {})
        self.assertEquals(encoded._raw, to_bin('0xff00 0000'))

    def test_encode_union_without_chosen_union_fails(self):
        union = self._get_foo_union()
        self.assertRaises(AssertionError, union.encode, {'foo.small': '0xff', 'foo.medium': '0xaaaa'}, {})

    def test_validate_union(self):
        union = self._get_foo_union()
        decoded = union.decode(to_bin('0xcafebabe'))
        self._should_pass(union.validate({'foo': decoded}, {'foo.small': '', 'foo.medium': ''}))
        self._should_fail(union.validate({'foo': decoded}, {'foo.small': '0xff', 'foo.medium': ''}), 1)

    def test_validate_struct_union(self):
        struct = get_pair()
        union = self._get_foo_union()
        struct.add(union)
        decoded = struct.decode(to_bin('0xcafebabe f00dd00d'))
        self._should_fail(struct.validate({'pair': decoded}, {}), 3)


class TestBinaryContainerTemplate(TestCase):

    def test_verify_field_length_fails(self):
        container = BinaryContainerTemplate('foo', None)
        container.add(Binary(3, 'threeBits', None))
        self.assertRaises(AssertionError, container.verify)

    def test_verify_single_byte_field_length_passes(self):
        container = BinaryContainerTemplate('foo', None)
        container.add(Binary(4, 'firstFour', None))
        container.add(Binary(4, 'lastFour', None))
        container.verify()

    def test_verify_multi_byte_field_length_passes(self):
        container = BinaryContainerTemplate('foo', None)
        for length, name in zip([4, 4, 5, 3, 1, 3, 12], ['a', 'b', 'c', 'd', 'e', 'f', 'g']):
            container.add(Binary(length, name, None))
        container.verify()

    def test_verify_only_binary_field_passes(self):
        container = BinaryContainerTemplate('foo', None)
        container.add(Binary(1, 'oneBit', None))
        self.assertRaises(AssertionError, container.add, UInt(2, 'intsNotAllowed', None))

    def test_decode_container(self):
        container = self._2_byte_container()
        decoded = container.decode(to_bin("0x9001"))
        self.assertEqual(1, decoded.oneBit.int)
        self.assertEqual(1, decoded.threeBits.int)
        self.assertEqual(1, decoded.twelveBits.int)

    def test_decode_little_endian_container(self):
        container = self._2_byte_container()
        decoded = container.decode(to_bin("0x0190"), little_endian=True)
        self.assertEqual(1, decoded.oneBit.int)
        self.assertEqual(1, decoded.threeBits.int)
        self.assertEqual(1, decoded.twelveBits.int)
        self.assertEquals(decoded._raw, to_bin("0x0190"))

    def test_encode_little_endian_container(self):
        container = self._2_byte_container()
        encoded = container.encode({'foo.threeBits': 1, 'foo.twelveBits': 1}, little_endian=True)
        self.assertEqual(1, encoded.oneBit.int)
        self.assertEqual(1, encoded.threeBits.int)
        self.assertEqual(1, encoded.twelveBits.int)
        self.assertEquals(encoded._raw, to_bin("0x0190"))

    def test_decode_longer_data_than_field(self):
        container = self._1_byte_container()
        decoded = container.decode(to_bin("0b0000 0001 1111 1111"))
        self.assertEqual(0, decoded.spare.int)
        self.assertEqual(1, decoded.value.int)

    def _1_byte_container(self):
        container = BinaryContainerTemplate('foo', None)
        container.add(Binary(4, 'spare', 0))
        container.add(Binary(4, 'value', 1))
        return container

    def _2_byte_container(self):
        container = BinaryContainerTemplate('foo', None)
        container.add(Binary(1, 'oneBit', 1))
        container.add(Binary(3, 'threeBits', 7))
        container.add(Binary(12, 'twelveBits', 4095))
        return container


class TestTBCDContainerTemplate(TestCase):

    def setUp(self):
        self._protocol = Protocol('TestProtocol')
        self._protocol.add(UInt(2, 'msgId', 5))
        self._protocol.add(UInt(2, 'length', None))
        self._protocol.add(PDU('length-4'))
        self.tmp = MessageTemplate('FooRequest', self._protocol, {})
        self.tmp.add(UInt(2, 'field_1', 1))
        self.tmp.add(UInt(2, 'field_2', 2))

    def test_verify_only_tbcd_number_passes(self):
        container = TBCDContainerTemplate('tbcd', None)
        container.add(TBCD('4', 'first', None))
        self.assertRaises(AssertionError, container.add, UInt(2, 'not allowed', None))

    def test_get_even_tbcd_field(self):
        container = TBCDContainerTemplate('tbcd', None)
        container.add(TBCD('4', 'first', '1234'))
        self.tmp.add(container)
        msg = self.tmp.encode({}, {})
        self.assertEqual('1234', msg.tbcd.first.tbcd)

    def test_get_odd_tbcd_field(self):
        container = TBCDContainerTemplate('tbcd', None)
        container.add(TBCD('3', 'first', '123'))
        self.tmp.add(container)
        msg = self.tmp.encode({}, {})
        self.assertEqual('123', msg.tbcd.first.tbcd)

    def test_get_binlength_for_odd_value_tbcd_container(self):
        container = TBCDContainerTemplate('tbcd', None)
        container.add(TBCD('1', 'first', '1'))
        self.assertEquals(8, container.binlength)
        container = TBCDContainerTemplate('tbcd', None)
        container.add(TBCD('3', 'first', '123'))
        self.assertEquals(16, container.binlength)

    def test_get_binlength_for_even_value_tbcd_container(self):
        container = TBCDContainerTemplate('tbcd', None)
        container.add(TBCD('2', 'first', '12'))
        self.assertEquals(8, container.binlength)
        container = TBCDContainerTemplate('tbcd', None)
        container.add(TBCD('4', 'first', '1234'))
        self.assertEquals(16, container.binlength)

    def test_decode(self):
        container = TBCDContainerTemplate('tbcd', None)
        container.add(TBCD('3', 'first', None))
        decoded = container.decode(to_bin('0x21f3'))
        self.assertEquals('123', decoded.first.tbcd)

    def test_little_endian_tbcd_unsupported(self):
        container = TBCDContainerTemplate('tbcd', None)
        container.add(TBCD('3', 'first', '123'))
        self.assertRaises(AssertionError, container.encode, {}, {}, little_endian=True)
        self.assertRaises(AssertionError, container.decode, to_bin('0x21f3'), little_endian=True)

    def test_get_encoded_raw_bytes(self):
        container = TBCDContainerTemplate('tbcd', None)
        container.add(TBCD('3', 'first', '123'))
        container.add(TBCD('13', 'second', '6100000000001'))
        encoded = container.encode({}, {})
        self.assertEquals(to_bin("0b0010000101100011000000010000000000000000000000000000000000010000"), encoded._get_raw_bytes())

    def test_decode_raw_bytes_with_star_length(self):
        container = TBCDContainerTemplate('tbcd', None)
        container.add(TBCD('3', 'first', '123'))
        container.add(TBCD('*', 'second', '6100000000001'))
        decoded = container.decode(to_bin("0b0010000101100011000000010000000000000000000000000000000000010000"))
        self.assertEquals('123', decoded.first.tbcd)
        self.assertEquals('6100000000001', decoded.second.tbcd)

    def test_encoded_even_value_container_returns_correct_length(self):
        container = TBCDContainerTemplate('tbcd', None)
        container.add(TBCD('3', 'first', '123'))
        container.add(TBCD('13', 'second', '6100000000001'))
        encoded = container.encode({})
        self.assertEquals(8, len(encoded))

    def test_encoded_odd_value_container_returns_correct_length(self):
        container = TBCDContainerTemplate('tbcd', None)
        container.add(TBCD('3', 'first', '456'))
        container.add(TBCD('4', 'second', '1234'))
        encoded = container.encode({})
        self.assertEquals(4, len(encoded))


class TestConditional(TestCase):

    def _get_conditional(self):
        struct = StructTemplate('Foo', 'foo', parent=None)
        struct.add(UInt(2, 'condition', 1))
        condition = ConditionalTemplate('condition==1', 'mycondition', None)
        condition.add(UInt(2, 'myvalue', 42))
        struct.add(condition)
        struct.add(UInt(2, 'second', 2))
        return struct

    def test_condition_is_false(self):
        cond = self._get_conditional()
        encoded = cond.encode({'foo.condition': 0}, None)
        self.assertEquals(encoded.mycondition.exists, False)

    def test_conditional_encode(self):
        cond = self._get_conditional()
        encoded = cond.encode({}, None)
        self.assertEquals(encoded.mycondition.exists, True)
        self.assertEquals(encoded.mycondition.myvalue.int, 42)

    def test_conditional_decode(self):
        cond = self._get_conditional()
        decoded = cond.decode(to_bin('0x00004242'))
        self.assertEquals(decoded.mycondition.exists, False)

    def test_conditional_decode_has_element(self):
        cond = self._get_conditional()
        decoded = cond.decode(to_bin('0x0001 000a 0043'))
        self.assertEquals(decoded.mycondition.exists, True)
        self.assertEquals(decoded.mycondition.myvalue.int, 10)


if __name__ == '__main__':
    main()
