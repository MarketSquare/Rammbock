import math
from binary_tools import to_0xhex, to_binary_string_of_length, to_bin_of_length, to_tbcd
from OrderedDict import OrderedDict


class _StructuredElement(object):

    def __init__(self, name):
        self._name = '%s %s' % (self._type, name)
        self._fields = OrderedDict()
        self._parent = None

    def __setitem__(self, name, child):
        self._fields[name] = child
        child._parent = self

    def __getitem__(self, name):
        return self._fields[str(name)]

    def __getattr__(self, name):
        return self[name]

    def __str__(self):
        return self._name

    def __repr__(self):
        result = '%s\n' % self._name
        for field in self._fields.values():
            result +=self._format_indented('%s' % repr(field))
        return result

    def __contains__(self, key):
        return key in self._fields

    def _format_indented(self, text):
        return ''.join(['  %s\n' % line for line in text.splitlines()])

    @property
    def _raw(self):
        return self._get_raw_bytes()
        
    def _get_raw_bytes(self):
        return ''.join((field._raw for field in self._fields.values()))

    def __len__(self):
        return sum(len(field) for field in self._fields.values())


class List(_StructuredElement):

    _type = 'List'

    def __init__(self, name, type_name):
        self._name = '%s %s[]' % (type_name, name)
        self._fields = OrderedDict()


class Struct(_StructuredElement):

    _type = 'Struct'

    def __init__(self, name, type_name):
        self._name = '%s %s' % (type_name, name)
        self._fields = OrderedDict()


class Union(_StructuredElement):

    _type = 'Union'

    def __init__(self, name, length):
        self._length = length
        _StructuredElement.__init__(self, name)

    def _get_raw_bytes(self):
        max_raw = ''
        for field in self._fields.values():
            if len(field._raw) > len(max_raw):
                max_raw = field._raw
        return max_raw.ljust(self._length, '\x00')


class BinaryContainer(_StructuredElement):

    _type = 'BinaryContainer'

    def _binlength(self):
        return sum(field.binlength for field in self._fields.values())

    def __len__(self):
        return self._binlength()/8

    def _get_raw_bytes(self):
        # TODO: faster implementation...
        return to_bin_of_length(len(self), ' '.join((field.bin for field in self._fields.values())))

class TBCDContainer(_StructuredElement):

    _type = 'TBCDContainer'

    def __len(selfs):
        return len("123456789")/2+len("123456789")%2


class Message(_StructuredElement):

    _type = 'Message'

    def _add_header(self, header):
        new = OrderedDict({'_header':header})
        new.update(self._fields)
        self._fields = new


class Header(_StructuredElement):

    _type = 'Header'


class Field(object):

    def __init__(self, type, name, value, aligned_len=None, little_endian=False):
        self._type = type
        self._name = name
        self._original_value = value
        self._length = aligned_len or len(value)
        self._little_endian = little_endian
        self._parent = None

    @property
    def _value(self):
        return self._original_value[::-1] if self._little_endian else self._original_value
    # TODO: If needed, original value and raw value can be precalculated
    # in __init__

    @property
    def name(self):
        return self._name

    @property
    def int(self):
        return int(self)

    def __int__(self):
        return int(to_0xhex(self._value), 16)

    @property
    def hex(self):
        return hex(self)

    @property
    def tbcd(self):
        return to_tbcd(self._original_value)

    def __hex__(self):
        return to_0xhex(self._value)

    @property
    def bytes(self):
        return self._value

    @property
    def chars(self):
        return str(self._value)

    @property
    def bin(self):
        return self._bin()

    def _bin(self):
        return to_binary_string_of_length(self._length*8, self._value)

    @property
    def ascii(self):
        return ''.join(i for i in self._value if 128 > ord(i) >= 32)

    @property
    def _raw(self):
        return self._original_value.ljust(self._length, '\x00')

    def __str__(self):
        return self.hex

    def __repr__(self):
        return '%s = %s' % (self.name, str(self))

    def __len__(self):
        return self._length


class BinaryField(Field):

    _type = 'binary'

    def __init__(self, length, name, value, aligned_len=None, little_endian=False):
        self._name = name
        self._original_value = value
        self._binlength = int(length)
        self._length = int(math.ceil(self._binlength/8.0))
        self._parent = None
        self._little_endian = False
        if little_endian:
            raise AssertionError('Not implemented yet')

    def _bin(self):
        return to_binary_string_of_length(self._binlength, self._value)

    @property
    def binlength(self):
        return self._binlength