import unittest
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..','src'))
from Protocol import Protocol, Length, UInt, PDU, MessageTemplate, MessageStream
from binary_conversions import to_bin_of_length, to_bin


class TestProtocol(unittest.TestCase):

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
        self._protocol.add(UInt(1, 'checksum', None))
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


class _MockStream(object):

    def __init__(self, data):
        self.data = data

    def read(self, length):
        result = self.data[:length]
        self.data = self.data[length:]
        return result


class TestProtocolMessageReceiving(unittest.TestCase):

    def setUp(self):
        self._protocol = Protocol('Test')
        self._protocol.add(UInt(1, 'id', 1))
        self._protocol.add(UInt(2, 'length', None))
        self._protocol.add(PDU('length-2'))

    def test_read_header_and_pdu(self):
        stream = _MockStream(to_bin('0xff0004cafe'))
        header, data = self._protocol.read(stream)
        self.assertEquals(header.id.hex, '0xff')
        self.assertEquals(data, '\xca\xfe')


class TestMessageStream(unittest.TestCase):

    def setUp(self):
        self._protocol = Protocol('Test')
        self._protocol.add(UInt(1, 'id', 1))
        self._protocol.add(UInt(2, 'length', None))
        self._protocol.add(PDU('length-2'))
        self._msg = MessageTemplate('FooRequest', self._protocol, {})
        self._msg.add(UInt(1, 'field_1', None))
        self._msg.add(UInt(1, 'field_2', None))

    def test_get_message(self):
        byte_stream = _MockStream(to_bin('0xff0004cafe aa0004dead'))
        msg_stream = MessageStream(byte_stream, self._protocol)
        msg = msg_stream.get(self._msg, {'id':'0xaa'})
        self.assertEquals(msg.field_1.hex, '0xde')

    def test_get_message_from_buffer(self):
        byte_stream = _MockStream(to_bin('0xff0004cafe aa0004dead'))
        msg_stream = MessageStream(byte_stream, self._protocol)
        _ = msg_stream.get(self._msg, {'id':'0xaa'})
        msg = msg_stream.get(self._msg, {})
        self.assertEquals(msg.field_1.hex, '0xca')


class TestMessageTemplate(unittest.TestCase):

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
        msg = self.tmp.encode({})
        self.assertEquals(msg.field_1.int, 1)
        self.assertEquals(msg.field_2.int, 2)

    def test_message_field_type_conversions(self):
        msg = self.tmp.encode({'field_1': 1024})
        self.assertEquals(msg.field_1.int, 1024)
        self.assertEquals(msg.field_1.hex, '0x0400')
        self.assertEquals(msg.field_1.bytes, '\x04\x00')

    def test_encode_template_with_params(self):
        msg = self.tmp.encode({'field_1':111, 'field_2':222})
        self.assertEquals(msg.field_1.int, 111)
        self.assertEquals(msg.field_2.int, 222)

    def test_encode_template_header(self):
        msg = self.tmp.encode({})
        self.assertEquals(msg._header.msgId.int, 5)
        self.assertEquals(msg._header.length.int, 8)

    def test_encode_to_bytes(self):
        msg = self.tmp.encode({})
        self.assertEquals(msg._header.msgId.int, 5)
        self.assertEquals(msg._raw, to_bin_of_length(8, '0x0005 0008 0001 0002'))

    # TODO: make the fields aware of their type?
    # so that uint fields are pretty printed to uints
    # bytes fields to hex bytes
    # and character fields to characters..
    def test_pretty_print(self):
        msg = self.tmp.encode({})
        self.assertEquals(msg._header.msgId.int, 5)
        self.assertEquals(str(msg), 'Message FooRequest')
        self.assertEquals(repr(msg),
'''Message FooRequest
  TestProtocol header
    msgId = 0x0005
    length = 0x0008
  field_1 = 0x0001
  field_2 = 0x0002
''')

    def test_unknown_params_cause_exception(self):
        self.assertRaises(Exception, self.tmp.encode, {'unknown':111})

    def test_decode_message(self):
        msg = self.tmp.decode(to_bin('0xcafebabe'))
        self.assertEquals(msg.field_1.hex, '0xcafe')


class TestFields(unittest.TestCase):

    def test_uint_static_field(self):
        field = UInt(5, "field", 8)
        self.assertTrue(field.length.static)
        self.assertEquals(field.name, "field")
        self.assertEquals(field.default_value, 8)
        self.assertEquals(field.type, 'uint')

    def test_pdu_field_without_subtractor(self):
        field = PDU('value')
        self.assertEquals(field.length.field, 'value')
        self.assertEquals(field.length.subtractor, 0)
        self.assertEquals(field.type, 'pdu')

    def test_pdu_field_without_subtractor(self):
        field = PDU('value-8')
        self.assertEquals(field.length.field, 'value')
        self.assertEquals(field.length.subtractor, 8)


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
