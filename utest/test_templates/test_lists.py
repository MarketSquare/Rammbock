from unittest import TestCase
from Rammbock.templates.primitives import UInt, PDU
from Rammbock.binary_tools import to_bin
from .tools import *


class TestListTemplate(TestCase):

    def test_create_list(self):
        list = get_list_of_three()
        self.assertEquals(list.name, 'topthree')
        self.assertEquals(list.encode({}, None)[0].int, 1)
        self.assertEquals(list.encode({}, None)[2].int, 1)

    def test_create_list_with_setting_value(self):
        list = get_list_of_three()
        encoded = list.encode({'topthree[0]': 42}, {}, None)
        self.assertEquals(encoded[0].int, 42)
        self.assertEquals(encoded[1].int, 1)

    def test_list_with_struct(self):
        list = get_struct_list()
        encoded = list.encode({'liststruct[1].first': 24}, {}, None)
        self.assertEquals(encoded[0].first.int, 1)
        self.assertEquals(encoded[1].first.int, 24)
        self.assertEquals(encoded[1].second.int, 2)

    def test_list_list(self):
        outerList = get_list_list()
        encoded = outerList.encode({'listlist[0][1]': 10, 'listlist[1][0]': 55}, {}, None)
        self.assertEquals(encoded[0][1].int, 10)
        self.assertEquals(encoded[1][0].int, 55)
        self.assertEquals(encoded[1][1].int, 7)

    def test_decode_message(self):
        list = ListTemplate('5', 'five', parent=None)
        list.add(UInt(4, None, 3))
        decoded = list.decode(to_bin('0x' + ('00000003' * 5)), {})
        self.assertEquals(len(decoded[4]), 4)
        self.assertEquals(len(decoded), 20)
        self.assertEquals(decoded[0].int, 3)

    def test_parse_params(self):
        list = get_list_of_three()
        params = list._get_params_sub_tree({'topthree[0]': 1, 'foo': 2, 'topthree[4][0]': 4})
        self.assertEquals(params['0'], 1)
        self.assertEquals(params['4[0]'], 4)
        self.assertEquals(len(params), 2)

    def test_parse_params_with_dot(self):
        list = get_list_of_three()
        params = list._get_params_sub_tree({'topthree.0': 1, 'foo': 2, 'topthree.4.0': 4})
        self.assertEquals(params['0'], 1)
        self.assertEquals(params['4.0'], 4)
        self.assertEquals(len(params), 2)

    def test_parse_params_with_dots_and_brackets(self):
        list = get_list_of_three()
        params = list._get_params_sub_tree({'topthree.0': 1, 'foo': 2, 'topthree.4[0]': 4})
        self.assertEquals(params['0'], 1)
        self.assertEquals(params['4[0]'], 4)
        self.assertEquals(len(params), 2)

    def test_set_list_values_with_defaults(self):
        pair_of_lists = get_struct_with_two_lists()
        encoded = pair_of_lists.encode({'pair.*': 2, 'pair.*[0]': 42})
        self.assertEquals(encoded.first_list[1].int, 2)
        self.assertEquals(encoded.second_list[1].int, 2)
        self.assertEquals(encoded.first_list[0].int, 42)
        self.assertEquals(encoded.second_list[0].int, 42)

    def test_pretty_print(self):
        encoded = get_struct_list().encode({}, None)
        self.assertEquals('\n' + repr(encoded),
                          """
Pair liststruct[]
  Pair 0
    first = 1 (0x0001)
    second = 2 (0x0002)
  Pair 1
    first = 1 (0x0001)
    second = 2 (0x0002)
""")

    def test_pretty_print_primitive_list(self):
        decoded = get_list_of_three().decode(to_bin('0x' + ('0003' * 3)), {})
        self.assertEquals('\n' + repr(decoded),
                          """
uint topthree[]
  0 = 3 (0x0003)
  1 = 3 (0x0003)
  2 = 3 (0x0003)
""")

    def test_pretty_print_list_list(self):
        decoded = get_list_list().decode(to_bin('0x' + ('0003' * 4)), {})
        self.assertEquals('\n' + repr(decoded),
                          """
List listlist[]
  uint 0[]
    0 = 3 (0x0003)
    1 = 3 (0x0003)
  uint 1[]
    0 = 3 (0x0003)
    1 = 3 (0x0003)
""")

    def test_not_enough_data(self):
        template = get_list_of_three()
        self.assertRaises(Exception, template.decode, to_bin('0x00010002'))
