from unittest import TestCase
from Rammbock.templates.containers import Protocol, MessageTemplate, StructTemplate, ListTemplate
from Rammbock.templates.primitives import UInt, PDU, Char
from Rammbock.binary_tools import to_bin


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
