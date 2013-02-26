from unittest import TestCase
from Rammbock.templates.containers import Protocol
from Rammbock.templates.primitives import UInt, PDU


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
