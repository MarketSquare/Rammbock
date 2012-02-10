import unittest
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..','src'))
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

class TestParamParsing(unittest.TestCase):

    def setUp(self):
        self.rammbock = Rammbock()

    def test_create_two_dicts(self):
        confs, fields = self.rammbock._parse_parameters(['foo=bar','doo:dar'])
        self.assertEquals(confs['foo'], 'bar')
        self.assertEquals(fields['doo'], 'dar')

    def test_use_shortest_name(self):
        confs, fields = self.rammbock._parse_parameters(['foo=this=is:config=value','doo:this=is:field'])
        self.assertEquals(confs['foo'], 'this=is:config=value')
        self.assertEquals(fields['doo'], 'this=is:field')

    def test_error_on_invalid_value(self):
        self.assertRaises(Exception, self.rammbock._parse_parameters, ['foo'])
