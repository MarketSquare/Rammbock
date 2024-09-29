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

from math import ceil
import math
import sys
import re

from Rammbock.message import Field, BinaryField
from Rammbock.binary_tools import to_bin_of_length, to_0xhex, to_tbcd_binary, \
    to_tbcd_value, to_bin, to_twos_comp, to_int
from robot.libraries.BuiltIn import BuiltIn
from robot.utils import PY3, is_bytes, py2to3


@py2to3
class _TemplateField(object):

    def __init__(self, name, default_value):
        self._set_default_value(default_value)
        self.name = name

    has_length = True
    can_be_little_endian = False
    referenced_later = False

    def get_static_length(self):
        if not self.length.static:
            raise IndexError('Length of %s is dynamic.' % self._get_name())
        return self.length.value

    def _get_element_value(self, paramdict, name=None):
        return paramdict.get(self._get_name(name), self.default_value)

    def _get_element_value_and_remove_from_params(self, paramdict, name=None):
        wild_card = paramdict.get('*') if not self.referenced_later else None
        return paramdict.pop(self._get_name(name),
                             self.default_value or wild_card)

    def encode(self, paramdict, parent, name=None, little_endian=False):
        value = self._get_element_value_and_remove_from_params(paramdict, name)
        if not value and self.referenced_later:
            return PlaceHolderField(self)
        return self._to_field(name, value, parent, little_endian=little_endian)

    def _to_field(self, name, value, parent, little_endian=False):
        field_name, field_value = self._encode_value(value, parent, little_endian=little_endian)
        return Field(self.type, self._get_name(name), field_name, field_value, little_endian=little_endian)

    def decode(self, data, message, name=None, little_endian=False):
        data = self._prepare_data(data)
        length, aligned_length = self.length.decode_lengths(message, len(data))
        if len(data) < aligned_length:
            raise Exception("Not enough data for '%s'. Needs %s bytes, given %s" % (self._get_recursive_name(message), aligned_length, len(data)))
        return Field(self.type,
                     self._get_name(name),
                     data[:length],
                     aligned_len=aligned_length,
                     little_endian=little_endian and self.can_be_little_endian)

    def _prepare_data(self, data):
        return BuiltIn().convert_to_bytes(data)

    def validate(self, parent, paramdict, name=None):
        name = name or self.name
        field = parent[name]
        value = field.bytes
        forced_value = self._get_element_value_and_remove_from_params(paramdict, name)
        forced_value_unicode = forced_value
        if PY3 and is_bytes(forced_value):
            forced_value_unicode = BuiltIn().convert_to_string(forced_value)
        try:
            if not forced_value_unicode or forced_value_unicode == 'None':
                return []
            elif forced_value_unicode.startswith('('):
                return self._validate_pattern(forced_value_unicode, value, field)
        except AttributeError as e:
            e.args = ('Validating {}:{} failed. {}.\n    Did you set default value as numeric object instead of string?'
                      .format(name, forced_value_unicode, e.args[0]),)
            raise e
        if forced_value_unicode.startswith('REGEXP'):
            return self._validate_regexp(forced_value_unicode, value, field)
        return self._validate_exact_match(forced_value, value, field)

    def _validate_regexp(self, forced_pattern, value, field):
        return ["Value of field '%s' can not be matched to regular expression pattern '%s'" %
                (field._get_recursive_name(), forced_pattern)]

    def _validate_pattern(self, forced_pattern, value, field):
        if self._validate_or(forced_pattern, value, field):
            return []
        if self._validate_masked(forced_pattern, value):
            return []
        return ["Value of field '%s' does not match pattern '%s!=%s'" %
                (field._get_recursive_name(), BuiltIn().convert_to_string(to_0xhex(value)), forced_pattern)]

    def _validate_or(self, forced_pattern, value, field):
        if forced_pattern.find('|') != -1:
            patterns = forced_pattern[1:-1].split('|')
            for pattern in patterns:
                if self._is_match(pattern, value, field._parent):
                    return True
            return False

    def _validate_masked(self, forced_pattern, value):
        if forced_pattern.find('&') != -1:
            masked_val, masked_field = self._apply_mask_to_values(forced_pattern, value)
            if masked_val == masked_field:
                return True
            return False

    def _apply_mask_to_values(self, forced_pattern, value):
        val = forced_pattern[1:-1].split('&')[0].strip()
        mask = forced_pattern[1:-1].split('&')[1].strip()
        return to_int(val) & to_int(mask), to_int(to_0xhex(value)) & to_int(mask)

    def _is_match(self, forced_value, value, parent):
        # TODO: Should pass msg
        forced_binary_val, _ = self._encode_value(forced_value, parent)
        return forced_binary_val == value

    def _validate_exact_match(self, forced_value, value, field):
        if not self._is_match(forced_value, value, field._parent):
            return ['Value of field %s does not match %s!=%s' %
                    (field._get_recursive_name(), BuiltIn().convert_to_string(self._default_presentation_format(value)), forced_value)]
        return []

    def _default_presentation_format(self, value):
        return to_0xhex(value)

    def _get_name(self, name=None):
        return name or self.name or self.type

    def _raise_error_if_no_value(self, value, parent):
        if value in (None, ''):
            raise AssertionError('Value of %s not set' % self._get_recursive_name(parent))

    def _get_recursive_name(self, parent):
        if not parent:
            return self.name
        return parent._get_recursive_name() + self.name

    def _set_default_value(self, value):
        self.default_value = BuiltIn().convert_to_string(value) if value and value != '""' else None


class PlaceHolderField(object):

    _type = 'referenced_later'
    _parent = None

    def __init__(self, template):
        self.template = template


class UInt(_TemplateField):

    type = 'uint'
    can_be_little_endian = True

    def __init__(self, length, name, default_value=None, align=None):
        _TemplateField.__init__(self, name, default_value)
        self.length = Length(length, align)

    def _encode_value(self, value, message, little_endian=False):
        self._raise_error_if_no_value(value, message)
        length, aligned_length = self.length.decode_lengths(message)
        binary = to_bin_of_length(length, value)
        binary = binary[::-1] if little_endian else binary
        return binary, aligned_length


class Int(UInt):

    type = 'int'
    can_be_little_endian = True

    def __init__(self, length, name, default_value=None, align=None):
        UInt.__init__(self, length, name, default_value, align)

    def _get_int_value(self, message, value):
        bin_len = self.length.decode_lengths(message)[0] * 8
        min = pow(-2, (bin_len - 1))
        max = pow(2, (bin_len - 1)) - 1
        if not min <= to_int(value) <= max:
            raise AssertionError('Value %s out of range (%d..%d)'
                                 % (value, min, max))
        return to_twos_comp(value, bin_len)

    def _encode_value(self, value, message, little_endian=False):
        self._raise_error_if_no_value(value, message)
        value = self._get_int_value(message, value)
        return UInt._encode_value(self, value, message, little_endian)


class Char(_TemplateField):

    type = 'chars'

    def __init__(self, length, name, default_value=None, terminator=None):
        _TemplateField.__init__(self, name, default_value)
        self._terminator = to_bin(terminator)
        self.length = Length(length)

    def _encode_value(self, value, message, little_endian=False):
        if isinstance(value, Field):
            value = value._value
        else:
            if not is_bytes(value):
                value = str(value or '')
                if PY3:
                    value = BuiltIn().convert_to_bytes(value)
            value += self._terminator
        length, aligned_length = self.length.find_length_and_set_if_necessary(message, len(value))
        return value.ljust(length, b'\x00'), aligned_length

    def _prepare_data(self, data):
        if PY3 and isinstance(data, str):
            data = data.encode("UTF-8")
        if self._terminator:
            return data[0:data.index(self._terminator) + len(self._terminator)]
        return data

    def _validate_regexp(self, forced_pattern, value, field):
        try:
            regexp = forced_pattern.split(':')[1].strip()
            if bool(re.match(regexp, field.ascii)):
                return []
            else:
                return ['Value of field %s does not match the RegEx %s!=%s' %
                        (field._get_recursive_name(), self._default_presentation_format(value), forced_pattern)]
        except re.error as e:
            raise Exception("Invalid RegEx Error : " + str(e))


class Binary(_TemplateField):

    type = 'bin'

    def __init__(self, length, name, default_value=None):
        _TemplateField.__init__(self, name, default_value)
        self.length = Length(length)
        if not self.length.static:
            raise AssertionError('Binary field length must be static. Length: %s' % length)

    def _encode_value(self, value, message, little_endian=False):
        self._raise_error_if_no_value(value, message)
        minimum_binary = to_bin(value)
        length, aligned = self.length.decode_lengths(message, len(minimum_binary))
        binary = to_bin_of_length(self._byte_length(length), value)
        return binary, self._byte_length(aligned)

    def _to_field(self, name, value, parent, little_endian=False):
        field_name, field_value = self._encode_value(value, parent, little_endian=little_endian)
        return BinaryField(self.length.value, self._get_name(name), field_name, field_value, little_endian=little_endian)

    def _byte_length(self, length):
        return int(ceil(length / 8.0))

    def _is_match(self, forced_value, value, message):
        forced_binary_val, _ = self._encode_value(forced_value, message)   # TODO: Should pass msg
        return int(to_0xhex(forced_binary_val), 16) == int(to_0xhex(value), 16)


class TBCD(_TemplateField):

    type = 'tbcd'

    def __init__(self, size, name, default_value):
        _TemplateField.__init__(self, name, default_value)
        self.length = Length(size)

    def _encode_value(self, value, message, little_endian=False):
        self._raise_error_if_no_value(value, message)
        binary = to_tbcd_binary(value)
        length = self.length.decode(message, len(binary))
        return binary, self._byte_length(length)

    def _default_presentation_format(self, value):
        return to_tbcd_value(value)

    def _byte_length(self, length):
        return int(ceil(length / 2.0))


class PDU(_TemplateField):

    type = 'pdu'
    name = '__pdu__'

    def __init__(self, length):
        self.length = Length(length)

    def encode(self, params, parent, little_endian=False):
        return None

    def validate(self, parent, paramdict, name=None):
        return []


def Length(value, align=None):
    value = str(value)
    if align:
        align = int(align)
    else:
        align = 1
    if align < 1:
        raise Exception('Illegal alignment %d' % align)
    elif value.isdigit():
        return _StaticLength(int(value), align)
    elif value == '*':
        return _FreeLength(align)
    return _DynamicLength(value, align)


class _Length(object):

    free = False

    def __init__(self):
        self.value = None
        self.align = None

    def decode_lengths(self, message, max_length=None):
        raise Exception("Override this method in implementing class.")

    def _get_aligned_lengths(self, length):
        return length, length + (self.align - length % self.align) % self.align

    def decode(self, message, maximum_length=None):
        """Decode the length of this field. Maximum length is the maximum
        length available from data or None if maximum length is not known.
        """
        return self.decode_lengths(message, maximum_length)[0]


class _StaticLength(_Length):
    static = True
    has_references = False

    def __init__(self, value, align):
        _Length.__init__(self)
        self.value = int(value)
        self.align = int(align)

    def decode_lengths(self, message, max_length=None):
        return self._get_aligned_lengths(self.value)

    def find_length_and_set_if_necessary(self, message, min_length, little_endian=False):
        return self._get_aligned_lengths(self.value)


class _FreeLength(_Length):
    static = False
    has_references = False
    free = True

    def __init__(self, align):
        self.align = int(align)

    def decode_lengths(self, message, max_length=None):
        if max_length is None:
            raise AssertionError('Free length (*) can only be used on context where maximum byte length is unambiguous')
        return self._get_aligned_lengths(max_length)

    def find_length_and_set_if_necessary(self, message, min_length):
        return self._get_aligned_lengths(min_length)


class _DynamicLength(_Length):
    static = False
    has_references = True

    def __init__(self, value, align):
        self.field, self.value_calculator = parse_field_and_calculator(value)
        self.field_parts = self.field.split('.')
        self.align = int(align)

    def calc_value(self, param):
        return self.value_calculator.calc_value(param)

    def solve_parameter(self, length):
        return self.value_calculator.solve_parameter(length)

    def decode_lengths(self, parent, max_length=None):
        reference = self._find_reference(parent)
        if not self._has_been_set(reference):
            raise AssertionError('Value of %s not set' % self.field)
        return self._get_aligned_lengths(self.calc_value(reference.int))

    def _find_reference(self, parent):
        field = self._get_field(parent)
        if field:
            return field
        else:
            parent = parent._parent
            return self._find_reference(parent) if parent else None

    def _get_field(self, elem):
        for part in self.field_parts:
            if part not in elem:
                return None
            elem = elem[part]
        return elem

    def _has_been_set(self, reference):
        return reference._type != 'referenced_later'

    def _set_length(self, reference, min_length, little_endian=False):
        value_len, aligned_len = self._get_aligned_lengths(min_length)
        reference._parent[self.field_parts[-1]] = \
            self._encode_ref_length(self.solve_parameter(aligned_len),
                                    reference,
                                    little_endian=little_endian)
        return value_len, aligned_len

    def _encode_ref_length(self, aligned_len, reference, little_endian=False):
        return reference.template.encode({self.field_parts[-1]: str(aligned_len)},
                                         reference._parent, little_endian=little_endian)

    def find_length_and_set_if_necessary(self, parent, min_length, little_endian=False):
        reference = self._find_reference(parent)
        if self._has_been_set(reference):
            self._raise_error_if_not_enough_space(reference, self.solve_parameter(min_length))
            return self._get_aligned_lengths(self.calc_value(reference.int))
        return self._set_length(reference, min_length, little_endian=little_endian)

    def _raise_error_if_not_enough_space(self, reference, min_length):
        if reference.int < min_length:
            raise IndexError("Value for length is too short")

    @property
    def value(self):
        raise IndexError('Length is dynamic.')


class IllegalDynamicLengthException(Exception):
    pass


def _partition(operator, value):
    return (val.strip() for val in value.rpartition(operator))


def parse_field_and_calculator(value):
    if "-" in value:
        field, _, subtractor = _partition('-', value)
        return field, Subtract(int(subtractor))
    elif "+" in value:
        field, _, add = _partition('+', value)
        return field, Adder(int(add))
    elif "*" in value:
        field, _, multiplier = _partition('*', value)
        return field, Multiplier(int(multiplier))
    return value.strip(), SingleValue()


class SingleValue(object):

    def calc_value(self, param):
        return param

    def solve_parameter(self, length):
        return length


class Subtract(object):

    def __init__(self, subtractor):
        self.subtractor = subtractor

    def calc_value(self, param):
        return param - self.subtractor

    def solve_parameter(self, length):
        return length + self.subtractor


class Adder(object):

    def __init__(self, add):
        self.add = add

    def calc_value(self, param):
        return param + self.add

    def solve_parameter(self, length):
        return length - self.add


class Multiplier(object):

    def __init__(self, multiplier):
        self.multiplier = multiplier

    def calc_value(self, param):
        return param * self.multiplier

    def solve_parameter(self, length):
        return math.ceil(length / float(self.multiplier))


class BagSize(object):

    fixed = re.compile(r'[1-9][0-9]*\Z')
    range = re.compile(r'([0-9]+)\s*-\s*([1-9][0-9]*)\Z')

    def __init__(self, size):
        # TODO: add open range 2-n
        size = size.strip()
        if size == '*':
            self._set_min_max(0, sys.maxsize)
        elif self.fixed.match(size):
            self._set_min_max(size, size)
        elif self.range.match(size):
            self._set_min_max(*self.range.match(size).groups())
        else:
            raise AssertionError("Invalid bag size %s." % size)

    def _set_min_max(self, min_, max_):
        self.min = int(min_)
        self.max = int(max_)
        if self.min > self.max:
            raise AssertionError("Invalid bag size %s." % str(self))

    def __str__(self):
        if self.min == self.max:
            return str(self.min)
        elif self.min == 0 and self.max == sys.maxsize:
            return '*'
        return '%s-%s' % (self.min, self.max)
