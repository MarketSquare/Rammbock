import socket
from contextlib import contextmanager
from Rammbock.templates.containers import Protocol, MessageTemplate, StructTemplate, ListTemplate, UnionTemplate, BinaryContainerTemplate, TBCDContainerTemplate, ConditionalTemplate
from Rammbock.templates.primitives import UInt, PDU, Char, Binary, TBCD


def get_empty_pair(name='pair'):
    struct = StructTemplate('Pair', name, parent=None)
    struct.add(UInt(2, 'first', None))
    struct.add(UInt(2, 'second', None))
    return struct


def get_struct_with_two_lists(name='pair'):
    struct = StructTemplate('PairOfLists', name, parent=None)
    struct.add(get_list_of_three('first_list', None))
    struct.add(get_list_of_three('second_list', None))
    return struct


def get_empty_recursive_struct():
    str_str = StructTemplate('StructStruct', '3pairs', parent=None)
    pair1 = get_empty_pair('pair1')
    pair2 = get_empty_pair('pair2')
    pair3 = get_empty_pair('pair3')
    str_str.add(pair1)
    str_str.add(pair2)
    str_str.add(pair3)
    return str_str


def get_pair():
    struct = StructTemplate('Pair', 'pair', parent=None)
    struct.add(UInt(2, 'first', 1))
    struct.add(UInt(2, 'second', 2))
    return struct


def get_recursive_struct():
    str_str = StructTemplate('StructStruct', 'str_str', parent=None)
    inner = get_pair()
    str_str.add(inner)
    return str_str


def get_list_of_three(name='topthree', value=1):
    list = ListTemplate(3, name, parent=None)
    list.add(UInt(2, None, value))
    return list


def get_list_list():
    innerList = ListTemplate(2, None, parent=None)
    innerList.add(UInt(2, None, 7))
    outerList = ListTemplate('2', 'listlist', parent=None)
    outerList.add(innerList)
    return outerList


def get_struct_list():
    list = ListTemplate(2, 'liststruct', parent=None)
    list.add(get_pair())
    return list


def get_struct_with_length_and_alignment():
    struct = StructTemplate('Pair', 'pair', parent=None, align=4)
    struct.add(UInt(2, 'first', 1))
    struct.add(UInt(1, 'second', 2))
    return struct


class MockStream(object):

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

    def return_data(self, data):
        self.data = data + self.data

    def empty(self):
        self.data = ''

    @contextmanager
    def sync_threads(self):
        yield


class WithValidation(object):

    def _should_pass(self, validation):
        self.assertEquals(validation, [])

    def _should_fail(self, validation, number_of_errors):
        self.assertEquals(len(validation), number_of_errors)
