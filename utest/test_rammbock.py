from unittest import TestCase, main
from Rammbock import Rammbock


class TestParamParsing(TestCase):

    def setUp(self):
        self.rammbock = Rammbock()

    def test_create_three_dicts(self):
        confs, pdu_fields, header_fields = self.rammbock._parse_parameters(['foo=bar', 'doo:dar'])
        self.assertEquals(confs['foo'], 'bar')
        self.assertEquals(pdu_fields['doo'], 'dar')

    def test_use_shortest_name(self):
        confs, pdu_fields, header_fields = self.rammbock._parse_parameters(['foo=this=is:config=value', 'doo:this=is:field'])
        self.assertEquals(confs['foo'], 'this=is:config=value')
        self.assertEquals(pdu_fields['doo'], 'this=is:field')

    def test_error_on_invalid_value(self):
        self.assertRaises(Exception, self.rammbock._parse_parameters, ['foo'])

    def test_parse_header_fields(self):
        confs, pdus, headers = self.rammbock._parse_parameters(['header:poo', 'header:doo:dar', 'header:foo:bar'])
        self.assertEquals(headers['doo'], 'dar')
        self.assertEquals(headers['foo'], 'bar')
        self.assertEquals(pdus['header'], 'poo')


LOCAL_IP = '127.0.0.1'

ports = {'SERVER_PORT': 12345,
         'CLIENT_PORT': 54321}


class TestMessageSequence(TestCase):

    def setUp(self):
        self.rammbock = Rammbock()

    def tearDown(self):
        self.rammbock.reset_rammbock()

    def _example_protocol(self):
        self.rammbock.new_protocol('TestProtocol')
        self.rammbock.uint(2, 'msgId', 5)
        self.rammbock.uint(2, 'length', None)
        self.rammbock.pdu('length-4')
        self.rammbock.end_protocol()

    def _foo_message(self):
        self.rammbock.new_message('FooRequest', 'TestProtocol')
        self.rammbock.uint(2, 'foo', '0xcafe')

    def _start_client_server(self, protocol=None):
        self.rammbock.start_udp_server(LOCAL_IP, ports['SERVER_PORT'],
                                       protocol=protocol, name='Server')
        self.rammbock.start_udp_client(LOCAL_IP, ports['CLIENT_PORT'],
                                       protocol=protocol, name='Client')
        self.rammbock.connect(LOCAL_IP, ports['SERVER_PORT'])

    def test_send_receive(self):
        self._example_protocol()
        self._start_client_server('TestProtocol')
        self._foo_message()
        self.rammbock.client_sends_message()
        self.rammbock.server_receives_message()
        self._sequence_should_equal(self.rammbock._message_sequence.get(),
                                    [['Client', 'Server', 'TestProtocol:FooRequest', '', 'received']])

    def test_validation_failure(self):
        self._example_protocol()
        self._start_client_server('TestProtocol')
        self._foo_message()
        self.rammbock.client_sends_message()
        try:
            self.rammbock.server_receives_message('foo:5')
        except:
            pass
        self._sequence_should_equal(self.rammbock._message_sequence.get(),
                                    [['Client', 'Server', 'TestProtocol:FooRequest', 'Value of field foo does not match 0xcafe!=5', 'received']])

    def test_send_binary_without_protocol(self):
        self._start_client_server()
        self.rammbock.client_sends_binary(b'foobar')
        self._sequence_should_equal(self.rammbock._message_sequence.get(),
                                    [['Client', '127.0.0.1:12345', 'binary', '', 'sent']])

    def test_receive_binary_without_protocol(self):
        self._start_client_server()
        self.rammbock.client_sends_binary(b'foobar')
        self.rammbock.server_receives_binary()
        self._sequence_should_equal(self.rammbock._message_sequence.get(),
                                    [['Client', 'Server', 'binary', '', 'received']])

    def _sequence_should_equal(self, seq_generator, expected):
        list_seq = [list(row) for row in seq_generator]
        self.assertEquals(list_seq, expected)


if __name__ == "__main__":
    main()
