from unittest import TestCase, main
from Rammbock.message_sequence import MessageSequence, SeqdiagGenerator

CLIENT = ('11.11.11.11', 11)
SERVER = ('11.11.11.11', 2222)


class TestMessageSequence(TestCase):

    def _send(self, seq):
        seq.send('Sender', CLIENT, SERVER, 'Protocol', 'Msg')

    def _receive(self, seq, error=''):
        seq.receive('Receiver', SERVER, CLIENT, 'Protocol', 'Msg', error=error)

    def test_register_send(self):
        seq = MessageSequence()
        self._send(seq)
        self._sequence_should_equal(seq.get(), [['Sender', '11.11.11.11:2222', 'Protocol:Msg', '', 'sent']])

    def test_register_receive(self):
        seq = MessageSequence()
        self._receive(seq)
        self._sequence_should_equal(seq.get(), [['11.11.11.11:11', 'Receiver', 'Protocol:Msg', '', 'received']])

    def test_register_operator(self):
        seq = MessageSequence()
        self._send(seq)
        self._operators_should_equal(seq.get_operators(), ['Sender', '11.11.11.11:2222'])

    def test_override_registered_operators_with_names(self):
        seq = MessageSequence()
        self._send(seq)
        self._receive(seq)
        self._operators_should_equal(seq.get_operators(), ['Sender', 'Receiver'])

    def test_register_send_and_receive(self):
        seq = MessageSequence()
        self._send(seq)
        self._receive(seq)
        self._sequence_should_equal(seq.get(), [['Sender', 'Receiver', 'Protocol:Msg', '', 'received']])

    def test_register_last_send_as_receive(self):
        seq = MessageSequence()
        self._send(seq)
        self._send(seq)
        self._receive(seq)
        self._sequence_should_equal(seq.get(), [['Sender', 'Receiver', 'Protocol:Msg', '', 'sent'],
                                    ['Sender', 'Receiver', 'Protocol:Msg', '', 'received']])

    def test_register_error(self):
        seq = MessageSequence()
        self._send(seq)
        self._receive(seq, error='We Fail!')
        self._sequence_should_equal(seq.get(), [['Sender', 'Receiver', 'Protocol:Msg', 'We Fail!', 'received']])

    def _sequence_should_equal(self, seq_generator, expected):
        list_seq = [list(row) for row in seq_generator]
        self.assertEquals(list_seq, expected)

    def _operators_should_equal(self, operator_generator, expected):
        self.assertEquals(list(operator_generator), expected)


class TestSeqdiagGenerator(TestCase):

    def setUp(self):
        self.generator = SeqdiagGenerator()

    def test_request_response(self):
        self.assertEquals(self.generator.generate(['Sender', 'Receiver'],
                          [['Sender', 'Receiver', 'Protocol:Msg', '', 'received'],
                           ['Receiver', 'Sender', 'Protocol:Msg', '', 'received']]),
                          """diagram {
    "Sender" -> "Receiver" [label = "Protocol:Msg"];
    "Sender" <- "Receiver" [label = "Protocol:Msg"];
}
""")

    def test_failure(self):
        self.assertEquals(self.generator.generate(['Sender', 'Receiver'],
                          [['Sender', 'Receiver', 'Protocol:Msg', 'This failed', 'received']]),
                          """diagram {
    "Sender" -> "Receiver" [label = "Protocol:Msg - This failed", color = red];
}
""")

    def test_several_operators(self):
        self.assertEquals(self.generator.generate(['Client', 'Server', 'DB'],
                          [['Client', 'Server', 'Protocol:Req', '', 'received'],
                           ['Server', 'Client', 'Protocol:Resp', '', 'received'],
                           ['Client', 'DB', 'msg', '', 'received'],
                           ['DB', 'Client', 'another', '', 'received'],
                           ['Server', 'DB', 'HTTP:background', '', 'received'],
                           ['DB', 'Server', 'HTTP:response', '', 'received']]),
                          """diagram {
    "Client" -> "Server" [label = "Protocol:Req"];
    "Client" <- "Server" [label = "Protocol:Resp"];
    "Client" -> "DB" [label = "msg"];
    "Client" <- "DB" [label = "another"];
    "Server" -> "DB" [label = "HTTP:background"];
    "Server" <- "DB" [label = "HTTP:response"];
}
""")

    def test_cutoff_at_15_operations(self):
        self.assertEquals(self.generator.generate(['Client', 'Server', 'DB'],
                          [['Client', 'Server', 'Protocol:Req', '', 'received'],
                           ['Server', 'Client', 'Protocol:Resp', '', 'received'],
                           ['Client', 'DB', 'msg', '', 'received'],
                           ['DB', 'Client', 'another', '', 'received'],
                           ['Server', 'DB', 'HTTP:background', '', 'received'],
                           ['DB', 'Server', 'HTTP:response', '', 'received']] * 10),
                          """diagram {
    "Client" <- "DB" [label = "another"];
    "Server" -> "DB" [label = "HTTP:background"];
    "Server" <- "DB" [label = "HTTP:response"];
    "Client" -> "Server" [label = "Protocol:Req"];
    "Client" <- "Server" [label = "Protocol:Resp"];
    "Client" -> "DB" [label = "msg"];
    "Client" <- "DB" [label = "another"];
    "Server" -> "DB" [label = "HTTP:background"];
    "Server" <- "DB" [label = "HTTP:response"];
    "Client" -> "Server" [label = "Protocol:Req"];
    "Client" <- "Server" [label = "Protocol:Resp"];
    "Client" -> "DB" [label = "msg"];
    "Client" <- "DB" [label = "another"];
    "Server" -> "DB" [label = "HTTP:background"];
    "Server" <- "DB" [label = "HTTP:response"];
}
""")


if __name__ == "__main__":
    main()
