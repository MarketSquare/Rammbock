import unittest
from Rammbock import Rammbock

class TestRammbock(unittest.TestCase):

    def setUp(self):
        self.rammbock = Rammbock()

    def test_starting_new_protocol_in_middle_of_old_fails(self):
        self.rammbock.start_protocol_description('foo')
        self.assertRaises(Exception, self.rammbock.start_protocol_description, 'bar')

    def test_redifining_protocol_fails(self):
        self.rammbock.start_protocol_description('foo')
        self.rammbock.uint(1,'length',None)
        self.rammbock.pdu('length')
        self.rammbock.end_protocol_description()
        self.assertRaises(Exception, self.rammbock.start_protocol_description, 'foo')

    def test_defining_message_when_defining_protocol(self):
        self.rammbock.start_protocol_description('foo')
        self.assertRaises(Exception, self.rammbock.new_message, 'foo')
