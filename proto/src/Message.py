from binary_conversions import to_0xhex

class Message(object):

    def __init__(self, name):
        self.__name = name
        self.__fields = []

    def __setitem__(self, name, value):
        self.__fields.append(Field(value[0], name, value[1]))

    def __getitem__(self, name):
        for field in self.__fields:
            if field.name == name:
                return field
        raise KeyError(name)

    def __getattr__(self, name):
        return self[name]

    def __str__(self):
        return 'Message %s' % self.__name

    def __repr__(self):
        result = 'Message %s %s\n' % (self.__name, str(self.__header))
        for field in self.__fields:
            result +='  %s\n' % repr(field)
        return result

    @property
    def _raw(self):
        return self.__header.raw


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

    def __str__(self):
        return self.hex

    def __repr__(self):
        return '%s = %s' % (self.name, str(self))
