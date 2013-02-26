from unittest import TestCase
from Rammbock.templates.containers import Protocol, MessageTemplate
from Rammbock.templates.primitives import UInt, PDU
from Rammbock.binary_tools import to_bin
from tools import *


class TestStructs(TestCase):

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