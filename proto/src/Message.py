from binary_conversions import to_0xhex


class _MessageStruct(object):
    def __init__(self, name):
        self._name = name
        self._fields = []

    def __setitem__(self, name, value):
        self._fields.append((name, value))

    def __getitem__(self, name):
        for field_name, field in self._fields:
            if field_name == name:
                return field
        raise KeyError(name)

    def __getattr__(self, name):
        return self[name]

    def __str__(self):
        return self._name

    def __repr__(self):
        result = '%s\n' % self._name
        for _, field in self._fields:
            result +=self._format_indented('%s' % repr(field))
        return result

    def _format_indented(self, text):
        return ''.join(['  %s\n' % line for line in text.splitlines()])

    @property
    def _raw(self):
        return ''.join((field._raw for _, field in self._fields))


class Message(_MessageStruct):

    def __init__(self, name):
        _MessageStruct.__init__(self, 'Message '+name)

    def _add_header(self, header):
        self._fields.insert(0, ('_header', header))


class MessageHeader(_MessageStruct):

    def __init__(self, name):
        _MessageStruct.__init__(self, name+' header')


class Field(object):

    def __init__(self, type, name, value):
        self._type = type
        self._name = name
        self._value = value

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

    def __hex__(self):
        return to_0xhex(self._value)

    @property
    def bytes(self):
        return self._value

    @property
    def chars(self):
        return str(self._value)

    #TODO: Test
    @property
    def ascii_chars(self):
        return ''.join(i for i in self._value if ord(i)<128 and ord(i)>=32)

    @property
    def _raw(self):
        return self._value

    def __str__(self):
        return self.hex

    def __repr__(self):
        return '%s = %s' % (self.name, str(self))
