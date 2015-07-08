from unittest import TestCase
from Rammbock.templates.primitives import UInt, PDU
from Rammbock.binary_tools import to_bin
from .tools import *


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
