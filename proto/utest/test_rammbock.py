import unittest

from Rammbock import Rammbock


class TestParamParsing(unittest.TestCase):

    def setUp(self):
        self.rammbock = Rammbock()

    def test_create_three_dicts(self):
        confs, pdu_fields, header_fields = self.rammbock._parse_parameters(['foo=bar','doo:dar'])
        self.assertEquals(confs['foo'], 'bar')
        self.assertEquals(pdu_fields['doo'], 'dar')

    def test_use_shortest_name(self):
        confs, pdu_fields, header_fields = self.rammbock._parse_parameters(['foo=this=is:config=value','doo:this=is:field'])
        self.assertEquals(confs['foo'], 'this=is:config=value')
        self.assertEquals(pdu_fields['doo'], 'this=is:field')

    def test_error_on_invalid_value(self):
        self.assertRaises(Exception, self.rammbock._parse_parameters, ['foo'])

    def test_parse_header_fields(self):
        confs, pdus, headers = self.rammbock._parse_parameters(['header:poo', 'header:doo:dar', 'header:foo:bar'])
        self.assertEquals(headers['doo'], 'dar')
        self.assertEquals(headers['foo'], 'bar')
        self.assertEquals(pdus['header'], 'poo')