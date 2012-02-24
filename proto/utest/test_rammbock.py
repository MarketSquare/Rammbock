import unittest

from Rammbock import Rammbock


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
