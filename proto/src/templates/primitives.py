from Message import Field, BinaryField
import math
from binary_tools import to_bin_of_length, to_0xhex


class _TemplateField(object):

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

    def decode(self, value, message, name=None, little_endian=False):
        length, aligned_length = self.length.decode_lengths(message)
        if len(value) < aligned_length: 
            raise Exception('Not enough data for %s. Needs %s bytes, given %s' % (self._get_name(name), aligned_length, len(value)))
        return Field(self.type, 
                     self._get_name(name), 
                     value[:length], 
                     aligned_len=aligned_length, 
                     little_endian=little_endian and self.can_be_little_endian)

    def validate(self, parent, paramdict, name=None):
        name = name or self.name
        field = parent[name]
        value = field.bytes
        forced_value = self._get_element_value_and_remove_from_params(paramdict, name)
        if not forced_value or forced_value == 'None':
            return []
        elif forced_value.startswith('('):
            return self._validate_pattern(forced_value, value, parent)
        return self._validate_exact_match(forced_value, value, parent)

    def _validate_pattern(self, forced_pattern, value, message):
        patterns = forced_pattern[1:-1].split('|')
        for pattern in patterns:
            if self._is_match(pattern, value, message):
                return []
        return ['Value of field %s does not match pattern %s!=%s' %
                (self._get_name(), to_0xhex(value), forced_pattern)]

    def _is_match(self, forced_value, value, message):
        forced_binary_val, _ = self._encode_value(forced_value, message)   # TODO: Should pass msg
        return forced_binary_val == value

    def _validate_exact_match(self, forced_value, value, message):
        if not self._is_match(forced_value, value, message):
            return ['Value of field %s does not match %s!=%s' %
                    (self._get_name(), to_0xhex(value), forced_value)]
        return []

    def _get_name(self, name=None):
        return name or self.name or self.type


class PlaceHolderField(object):

    _type = 'referenced_later'
    _parent = None

    def __init__(self, template):
        self.template = template


class UInt(_TemplateField):

    type = 'uint'
    can_be_little_endian = True    

    def __init__(self, length, name, default_value=None, align=None):
        self.length = Length(length, align)
        self.name = name
        self.default_value = str(default_value) if default_value and default_value != '""' else None

    def _encode_value(self, value, message, little_endian=False):
        if not value:
            raise AssertionError('Value of %s not set' % self._get_name())
        length, aligned_length = self.length.decode_lengths(message)
        binary = to_bin_of_length(length, value)
        binary = binary[::-1] if little_endian else binary
        return binary, aligned_length


class Char(_TemplateField):

    type = 'char'

    def __init__(self, length, name, default_value=None):
        self.length = Length(length)
        self.name = name
        self.default_value = default_value if default_value and default_value != '""' else None

    def _encode_value(self, value, message, little_endian=False):
        value = value or ''
        length, aligned_length = self.length.find_length_and_set_if_necessary(message, len(value))
        return str(value).ljust(length,'\x00'), aligned_length


class Binary(_TemplateField):

    type = 'binary'

    def __init__(self, length, name, default_value=None):
        self.length = Length(length)
        if not self.length.static:
            raise AssertionError('Binary field length must be static. Length: %s' % length)
        self.name = name
        self.default_value = str(default_value) if default_value and default_value != '""' else None

    def _encode_value(self, value, message, little_endian=False):
        if not value:
            raise AssertionError('Value of %s not set' % self._get_name())
        length, aligned = self.length.decode_lengths(message)
        binary = to_bin_of_length(self._byte_length(length), value)
        return binary, self._byte_length(aligned)

    def _to_field(self, name, value, parent, little_endian=False):
        field_name, field_value = self._encode_value(value, parent, little_endian=little_endian)
        return BinaryField(self.length.value, self._get_name(name), field_name, field_value, little_endian=little_endian)

    def _byte_length(self, length):
        return int(math.ceil(length/8.0))


class PDU(_TemplateField):

    type = 'pdu'
    name = '__pdu__'

    def __init__(self, length):
        self.length = Length(length)

    def encode(self, params, parent, little_endian=False):
        return None


def Length(value, align=None):
    if align:
        align = int(align)
    else:
        align = 1
    if align < 1:
        raise Exception('Illegal alignment %d' % align)
    if str(value).isdigit():
        return _StaticLength(int(value), align)
    return _DynamicLength(value, align)


class _Length(object):
    
    def _get_aligned_lengths(self, length):
        return (length, length + (self.align - length % self.align) % self.align)

    def decode(self, message):
        return self.decode_lengths(message)[0]


class _StaticLength(_Length):
    static = True

    def __init__(self, value, align):
        self.value = int(value)
        self.align = int(align)

    def decode_lengths(self, message):
        return self._get_aligned_lengths(self.value)

    def find_length_and_set_if_necessary(self, message, min_length):
        return self.decode_lengths(message)


class _DynamicLength(_Length):
    static = False

    def __init__(self, value, align):
        if "-" in value:
            self.field, _, subtractor = value.rpartition('-')
        else:
            self.field, subtractor = value, 0
        self.subtractor = int(subtractor)
        self.align = int(align)

    def calc_value(self, param):
        return param - self.subtractor

    def solve_parameter(self, length):
        return length + self.subtractor

    def decode_lengths(self, parent):
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
        reference._parent[self.field] = reference.template.encode({self.field:str(aligned_len)}, reference._parent)
        return value_len, aligned_len

    def find_length_and_set_if_necessary(self, parent, min_length):
        reference = self._find_reference(parent)
        if self._has_been_set(reference):
            if self._check_enough_space(parent, reference, min_length):
                raise Exception("Value for length is too short")
            return self.decode_lengths(parent)
        return self._set_length(reference, min_length)

    def _check_enough_space(self, parent, reference, min_length):
        return reference._length < min_length if not parent[self.field] else\
        parent[self.field].int < min_length > reference._length

    @property
    def value(self):
        raise Exception('Length is dynamic.')