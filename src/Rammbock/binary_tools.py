#  Copyright 2014 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import binascii
import struct

from robot.libraries.BuiltIn import BuiltIn

try:
    if bin(0):
        pass
except NameError as name_error:
    def bin(value):
        """
        Support for Python 2.5
        Based on a recipe by Benjamin Wiley Sittler.
        http://code.activestate.com/recipes/219300-format-integer-as-binary-string/
        """
        if value < 0:
            return '-' + bin(-value)
        out = []
        if value == 0:
            out.append('0')
        while value > 0:
            out.append('01'[value & 1])
            value >>= 1
        try:
            return '0b' + ''.join(reversed(out))
        except NameError:
            out.reverse()
        return '0b' + ''.join(out)

LONGLONG = struct.Struct('>Q')


def to_bin(string_value):
    if string_value in (None, ''):
        return b''
    string_value = BuiltIn().convert_to_string(string_value)
    if string_value.startswith('0x'):
        return _hex_to_bin(string_value)
    elif string_value.startswith('0b'):
        return _int_to_bin(int(string_value.replace('0b', '')
                                           .replace(' ', ''), 2))
    return _int_to_bin(int(string_value))


def _int_to_bin(integer):
    if integer >= 18446744073709551616:
        return to_bin(hex(integer))
    return LONGLONG.pack(integer).lstrip(b'\x00') or b'\x00'


def _hex_to_bin(string_value):
    value = string_value.replace('0x', '').replace(' ', '').replace('L', '')
    if len(value) % 2 == 1:
        value = '0' + value
    return binascii.unhexlify(value)


def to_bin_of_length(length, string_value):
    bin = to_bin(string_value)
    if len(bin) > length:
        raise AssertionError('Too long binary value %s (max length %d)'
                             % (string_value, length))
    return bin.rjust(length, b'\x00')


def to_hex(binary):
    return binascii.hexlify(binary)


def to_0xhex(binary):
    return b'0x' + to_hex(binary)


def to_binary_string_of_length(length, bytes):
    result = bin(int(to_0xhex(bytes), 16))
    if len(result) < length + 2:
        result = '0b' + '0' * (length - len(result) + 2) + result[2:]
    return result


def to_bin_str_from_int_string(length, value):
    return to_binary_string_of_length(length, to_bin(value))[2:]


def to_tbcd_value(binary):
    bin_str, value = to_binary_string_of_length(len(to_hex(binary)) *
                                                4, binary), ""
    for index in range(2, len(bin_str), 8):
        if int(bin_str[index:index + 4], 2) == 15:
            return value + str(int(bin_str[index + 4: index + 8], 2))
        value += "%s%s" % (int(bin_str[index + 4:index + 8], 2),
                           int(bin_str[index: index + 4], 2))
    return value


def to_tbcd_binary(tbcd_string):
    value, index = "0b", 0
    while index <= len(tbcd_string) - 2:
        value += to_bin_str_from_int_string(4, tbcd_string[index + 1]) +\
            to_bin_str_from_int_string(4, tbcd_string[index])
        index += 2
    return to_bin(value if index == len(tbcd_string)
                  else value + to_bin_str_from_int_string(4, 15) +
                  to_bin_str_from_int_string(4, tbcd_string[index]))


def to_twos_comp(val, bits):
    """compute the 2's compliment of int value val"""
    if not val.startswith('-'):
        return to_int(val)
    value = _invert(to_bin_str_from_int_string(bits, bin(to_int(val[1:]))))
    return int(value, 2) + 1


def from_twos_comp(val, bits):
    """compute the 2's compliment of int value val"""
    if val & (1 << (bits - 1)):
        val -= 1 << bits
    return val


def _invert(value):
    return "".join(str(int(a) ^ 1) for a in value)


def to_int(string_value):
    if string_value in (None, '', b''):
        raise Exception("No value or empty value given")
    string_value = BuiltIn().convert_to_string(string_value)
    if string_value.startswith('0x') or string_value[:3] == '-0x':
        return int(string_value, 16)
    elif string_value.startswith('0b') or string_value[:3] == '-0b':
        return int(string_value, 2)
    return int(string_value)
