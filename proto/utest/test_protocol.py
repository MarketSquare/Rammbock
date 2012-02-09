import unittest
from Protocol import Protocol
from Protocol import Length

class TestProtocol(unittest.TestCase):

    def setUp(self, *args, **kwargs):
        self._protocol = Protocol()

    def test_header_length(self):
        self._protocol.uint(1, 'name1', None)
        self.assertEquals(self._protocol.header_length(), 1)

    def test_header_length_with_pdu(self):
        self._protocol.uint(1, 'name1', None)
        self._protocol.uint(2, 'name2', 5)
        self._protocol.uint(2, 'length', None)
        self._protocol.pdu('length')
        self._protocol.uint(1, 'checksum', None)
        self.assertEquals(self._protocol.header_length(), 5)

    def test_verify_undefined_length(self):
        self._protocol.uint(1, 'name1', None)
        self._protocol.uint(2, 'name2', 5)
        self.assertRaises(Exception, self._protocol.pdu, 'length')

    def test_verify_calculated_length(self):
        self._protocol.uint(1, 'name1', 1)
        self._protocol.uint(2, 'length', None)
        self._protocol.pdu('length-8')
        self.assertEquals(self._protocol.header_length(), 3)


class TestLength(unittest.TestCase):

    def test_create_length(self):
        length = Length('5')
        self.assertTrue(length.static)

    def test_create_length(self):
        length = Length('length')
        self.assertFalse(length.static)

    def test_static_length(self):
        length = Length('5')
        self.assertEquals(length.value, 5)

    def test_only_one_variable_in_dynamic_length(self):
        self.assertRaises(Exception,Length,'length-messageId')

    def test_dynamic_length(self):
        length = Length('length-8')
        self.assertEquals(length.solve_value(18), 10)
        self.assertEquals(length.solve_parameter(10), 18)

    def test_dynamic_length(self):
        length = Length('length')
        self.assertEquals(length.solve_value(18), 18)
        self.assertEquals(length.solve_parameter(18), 18)

    def test_get_field_name(self):
        length = Length('length-8')
        self.assertEquals(length.field, 'length')
