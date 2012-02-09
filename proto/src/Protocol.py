from Message import Message
from binary_conversions import to_bin_of_length

class _Template(object):

    def add(self, field):
        if not field.length.static:
            if not field.length.field in [elem.name for elem in self._fields]:
                raise Exception('Length field %s unknown' % length.field)
        self._fields.append(field)


class Protocol(_Template):

    def __init__(self, name):
        self._fields = []
        self.name = name

    def header_length(self):
        length = 0
        for field in self._fields:
            if not field.length.static:
                return length
            length += field.length.value
        return length


class MessageTemplate(_Template):

    def __init__(self, message_name, protocol, header_params):
        self._protocol = protocol
        self._message_name = message_name
        self._header_parameters = header_params
        self._fields= []

    def encode(self, message_params):
        message_params = message_params.copy()
        msg = Message(self._message_name)
        for field in self._fields:
            msg[field.name] = (field.type, field.encode(message_params))
        if message_params:
            raise Exception('Unknown fields %s' % str(message_params))
        return msg

class UInt(object):

    type = 'uint'

    def __init__(self, length, name, default_value):
        self.length = Length(length)
        self.name = name
        self.default_value = default_value

    def encode(self, paramdict):
        value = self._get_element_value_and_remove_from_params(paramdict)
        return to_bin_of_length(self.length.value, value)

    def _get_element_value_and_remove_from_params(self, paramdict):
        return paramdict.pop(self.name, self.default_value)


class PDU(object):

    type = 'pdu'

    def __init__(self, length):
        self.length = Length(length)


def Length(value):
    if str(value).isdigit():
        return _StaticLength(int(value))
    return _DynamicLength(value)


class _StaticLength(object):
    static = True

    def __init__(self, value):
        self.value = value


class _DynamicLength(object):
    static = False

    def __init__(self, value):
        if "-" in value:
            self.field, _, subtractor = value.rpartition('-')
        else:
            self.field, subtractor = value, 0
        self.subtractor = int(subtractor)

    def solve_value(self, param):
        return param - self.subtractor

    def solve_parameter(self, length):
        return length + self.subtractor


