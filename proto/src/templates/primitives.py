from Message import Field
from binary_conversions import to_bin_of_length, to_0xhex


class _TemplateField(object):

    has_length = True
    
    def get_static_length(self):
        if not self.length.static:
            raise Exception('Length of %s is dynamic.' % self._get_name())
        return self.length.value
    
    def _get_element_value(self, paramdict, name=None):
        return paramdict.get(self._get_name(name), self.default_value)

    def _get_element_value_and_remove_from_params(self, paramdict, name=None):
        return paramdict.pop(self._get_name(name), self.default_value)

    def encode(self, paramdict, parent, name=None):
        value = self._get_element_value_and_remove_from_params(paramdict, name)
        return Field(self.type,self._get_name(name), self._encode_value(value, parent))

    def decode(self, value, message, name=None):
        decoded_length = self.length.decode(message)
        if len(value) < decoded_length: 
            raise Exception('Not enough data for %s. Needs %s bytes, given %s' % (name, self.length.value, len(value)))
        return Field(self.type, self._get_name(name), value[:decoded_length])

    def validate(self, parent, paramdict, name=None):
        name = name if name else self.name
        field = parent[name]
        value = field.bytes
        forced_value = self._get_element_value(paramdict, name)
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
        forced_binary_val = self._encode_value(forced_value, message)   # TODO: Should pass msg
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

    def __init__(self, length, name, default_value=None):
        self.length = Length(length)
        self.name = name
        self.default_value = str(default_value) if default_value and default_value != '""' else None

    def _encode_value(self, value, message):
        if not value:
            raise AssertionError('Value of %s not set' % self._get_name())
        return to_bin_of_length(self.length.value, value)


class Char(_TemplateField):

    type = 'char'

    def __init__(self, length, name, default_value=None):
        self.length = Length(length)
        self.name = name
        self.default_value = default_value if default_value and default_value != '""' else None

    def _encode_value(self, value, message):
        value = value if value else ''
        return str(value).ljust(self.length.decode(message), '\x00')


class PDU(_TemplateField):

    type = 'pdu'

    def __init__(self, length):
        self.length = Length(length)

    def encode(self, params, parent):
        return None


def Length(value):
    if str(value).isdigit():
        return _StaticLength(int(value))
    return _DynamicLength(value)


class _StaticLength(object):
    static = True

    def __init__(self, value):
        self.value = value

    def decode(self, message):
        return self.value


class _DynamicLength(object):
    static = False

    def __init__(self, value):
        if "-" in value:
            self.field, _, subtractor = value.rpartition('-')
        else:
            self.field, subtractor = value, 0
        self.subtractor = int(subtractor)

    def calc_value(self, param):
        return param - self.subtractor

    def solve_parameter(self, length):
        return length + self.subtractor

    def decode(self, message):
        return self.calc_value(message[self.field].int)

    @property
    def value(self):
        raise Exception('Length is dynamic.')