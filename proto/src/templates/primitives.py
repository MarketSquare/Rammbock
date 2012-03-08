from Message import Field
from binary_tools import to_bin_of_length, to_0xhex


class _TemplateField(object):

    has_length = True
    can_be_little_endian = False
    
    def get_static_length(self):
        if not self.length.static:
            raise Exception('Length of %s is dynamic.' % self._get_name())
        return self.length.value
    
    def _get_element_value(self, paramdict, name=None):
        return paramdict.get(self._get_name(name), self.default_value)

    def _get_element_value_and_remove_from_params(self, paramdict, name=None):
        return paramdict.pop(self._get_name(name),
            self.default_value or paramdict.get('*'))

    def encode(self, paramdict, parent, name=None, little_endian=False):
        value = self._get_element_value_and_remove_from_params(paramdict, name)
        field_name, field_value = self._encode_value(value, parent, little_endian=little_endian)
        return Field(self.type,self._get_name(name), field_name, field_value, little_endian=little_endian)

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
        name = name if name else self.name
        field = parent[name]
        value = field.bytes
        forced_value = self._get_element_value_and_remove_from_params(paramdict, name)
        if not forced_value or forced_value == 'None':
            return []
        if forced_value.startswith('('):
            return self._validate_pattern(forced_value, value, parent)
        else:
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
        value = value if value else ''
        length, aligned_length = self.length.decode_lengths(message)
        return str(value).ljust(length,'\x00'), aligned_length


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
        self.value = value
        self.align = align

    def decode_lengths(self, message):
        return self._get_aligned_lengths(self.value)

class _DynamicLength(_Length):
    static = False

    def __init__(self, value, align):
        if "-" in value:
            self.field, _, subtractor = value.rpartition('-')
        else:
            self.field, subtractor = value, 0
        self.subtractor = int(subtractor)
        self.align = align

    def calc_value(self, param):
        return param - self.subtractor

    def solve_parameter(self, length):
        return length + self.subtractor

    def decode_lengths(self, message):
        return self._get_aligned_lengths(self.calc_value(message[self.field].int))

    @property
    def value(self):
        raise Exception('Length is dynamic.')