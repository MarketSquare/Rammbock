import unittest
import socket

from templates.message_stream import MessageStream
from templates import Protocol, MessageTemplate, UInt, PDU
from binary_tools import to_bin 


class _MockStream(object):

    def __init__(self, data):
        self.data = data

    def read(self, length, timeout=None):
        if length > len(self.data):
            if timeout:
                raise socket.timeout('timeout')
            else:
                raise AssertionError('No timeout, but out of data.')
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
        self._msg = MessageTemplate('FooRequest', self._protocol, {'id':'0xaa'})
        self._msg.add(UInt(1, 'field_1', None))
        self._msg.add(UInt(1, 'field_2', None))

    def test_get_message(self):
        byte_stream = _MockStream(to_bin('0xff0004cafe aa0004dead'))
        msg_stream = MessageStream(byte_stream, self._protocol)
        msg = msg_stream.get(self._msg)
        self.assertEquals(msg.field_1.hex, '0xde')

    def test_get_message_from_buffer(self):
        byte_stream = _MockStream(to_bin('0xff0004cafe aa0004dead'))
        msg_stream = MessageStream(byte_stream, self._protocol)
        _ = msg_stream.get(self._msg)
        self._msg.header_parameters = {}
        msg = msg_stream.get(self._msg)
        self.assertEquals(msg.field_1.hex, '0xca')

    def test_timeout_goes_to_stream(self):
        byte_stream = _MockStream(to_bin('0xff0004cafe aa0004dead'))
        msg_stream = MessageStream(byte_stream, self._protocol)
        self._msg.header_parameters = {'id':'0x00'}
        self.assertRaises(socket.timeout, msg_stream.get, self._msg, timeout=1)


if __name__ == '__main__':
    unittest.main()
