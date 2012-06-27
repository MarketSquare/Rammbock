#  Copyright 2012 Nokia Siemens Networks Oyj
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

from Rammbock.message import Field, BinaryField
from Rammbock.binary_tools import to_bin_of_length, to_0xhex, to_tbcd_binary, \
    to_tbcd_value, to_bin, to_twos_comp


class _TemplateField(object):

    def __init__(self, name, default_value):
        self._set_default_value(default_value)
        self.name = name

    has_length = True
    can_be_little_endian = False
    referenced_later = False

    def get_static_length(self):
        if not self.length.static:
            raise Exception('Length of %s is dynamic.' % self._get_name())
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
        return data

    def validate(self, parent, paramdict, name=None):
        name = name or self.name
        field = parent[name]
        value = field.bytes
        forced_value = self._get_element_value_and_remove_from_params(paramdict, name)
        if not forced_value or forced_value == 'None':
            return []
        elif forced_value.startswith('('):
            return self._validate_pattern(forced_value, value, field)
        return self._validate_exact_match(forced_value, value, field)

    def _validate_pattern(self, forced_pattern, value, field):
        patterns = forced_pattern[1:-1].split('|')
        for pattern in patterns:
            if self._is_match(pattern, value, field._parent):
                return []
        return ["Value of field '%s' does not match pattern '%s!=%s'" %
                (field._get_recursive_name(), to_0xhex(value), forced_pattern)]

    def _is_match(self, forced_value, value, parent):
        #TODO: Should pass msg
        forced_binary_val, _ = self._encode_value(forced_value, parent)
        return forced_binary_val == value

    def _validate_exact_match(self, forced_value, value, field):
        if not self._is_match(forced_value, value, field._parent):
            return ['Value of field %s does not match %s!=%s' %
                    (field._get_recursive_name(), self._default_presentation_format(value), forced_value)]
        return []

    def _default_presentation_format(self, value):
        return to_0xhex(value)

    def _get_name(self, name=None):
        return name or self.name or self.type

    def _raise_error_if_no_value(self, value, parent):
        if not value:
            raise AssertionError('Value of %s not set' % self._get_recursive_name(parent))

    def _get_recursive_name(self, parent):
        if not parent:
            return self.name
        return parent._get_recursive_name() + self.name

    def _set_default_value(self, value):
        self.default_value = str(value) if value and value != '""' else None


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


class SInt(_TemplateField):

    type = 'sint'
    can_be_little_endian = False

    def __init__(self, length, name, default_value=None, align=None):
        _TemplateField.__init__(self, name, default_value)
        self.length = Length(length, align)

    def _encode_value(self, value, message, little_endian=False):
        self._raise_error_if_no_value(value, message)
        length, aligned_length = self.length.decode_lengths(message)
        value = to_twos_comp(value, length * 8)
        binary = to_bin_of_length(length, value)
        binary = binary[::-1] if little_endian else binary
        return binary, aligned_length


class Char(_TemplateField):

    type = 'chars'

    def __init__(self, length, name, default_value=None, terminator=None):
        _TemplateField.__init__(self, name, default_value)
        self._terminator = to_bin(terminator)
        self.length = Length(length)

    def _encode_value(self, value, message, little_endian=False):
        value = value or ''
        value += self._terminator
        length, aligned_length = self.length.find_length_and_set_if_necessary(message, len(value))
        return str(value).ljust(length, '\x00'), aligned_length

    def _prepare_data(self, data):
        if self._terminator:
            return data[0:data.index(self._terminator) + 1]
        return data


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

    def find_length_and_set_if_necessary(self, message, min_length):
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
        if self.field in parent:
            return parent[self.field]
        return self._find_reference(parent._parent) or None

    def _has_been_set(self, reference):
        return reference._type != 'referenced_later'

    def _set_length(self, reference, min_length):
        value_len, aligned_len = self._get_aligned_lengths(min_length)
        reference._parent[self.field] = self._encode_ref_length(aligned_len,
                                                                reference)
        return value_len, aligned_len

    def _encode_ref_length(self, aligned_len, reference):
        return reference.template.encode({self.field: str(aligned_len)},
                                         reference._parent)

    def find_length_and_set_if_necessary(self, parent, min_length):
        min_value_for_reference = self.solve_parameter(min_length)
        reference = self._find_reference(parent)
        if self._has_been_set(reference):
            self._raise_error_if_not_enough_space(reference, min_value_for_reference)
            return self._get_aligned_lengths(self.calc_value(reference.int))
        return self._set_length(reference, min_value_for_reference)

    def _raise_error_if_not_enough_space(self, reference, min_length):
        if reference.int < min_length:
            raise Exception("Value for length is too short")

    @property
    def value(self):
        raise Exception('Length is dynamic.')


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
