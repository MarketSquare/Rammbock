from unittest import TestCase
from Rammbock.templates.primitives import UInt, PDU
from Rammbock.binary_tools import to_bin
from .tools import *


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
