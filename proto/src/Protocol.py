UINT = 'uint'
PDU = 'pdu'

class Protocol(object):

    def __init__(self):
        self._fields = []

    def uint(self, length, name, value):
        self._fields.append((UINT, Length(length), name, value))

    def header_length(self):
        length = 0
        for field in self._fields:
            if field[0] == PDU:
                return length
            length += field[1]
        return length

    def pdu(self, length_param):
        length = Length(length_param)
        name = length.split("-")[0]
        if not name in [field[2] for field in self._fields]:
            raise Exception('PDU length field %s unknown' % length)
        self._fields.append((PDU, self._get_field_length(name), None, None))

    def _get_field_length(self, name):
        for field in self._fields:
            if field[2] == name:
                return field[1]


def Length(value):
    if value.isdigit():
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


