import unittest
from message_sequence import MessageSequence

CLIENT = ('11.11.11.11', 11)
SERVER = ('11.11.11.11', 2222)

class TestMessageSequence(unittest.TestCase):

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

