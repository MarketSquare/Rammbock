from Message import Field, Message, MessageHeader
from binary_conversions import to_bin_of_length, to_bin, to_hex, to_0xhex

class _Template(object):

    def __init__(self, name):
        self._fields = []
        self.name = name

    def add(self, field):
        if not field.length.static:
            if not field.length.field in [elem.name for elem in self._fields]:
                raise Exception('Length field %s unknown' % length.field)
        self._fields.append(field)

    def _encode_fields(self, struct, params):
        for field in self._fields:
            # TODO: clean away this ugly hack that makes it possible to skip PDU
            # (now it is a 0 length place holder in header)
            encoded = field.encode(params)
            if encoded:
                struct[field.name] = Field(field.type, field.name, encoded)
        if params:
            raise Exception('Unknown fields in header %s' % str(params))


class Protocol(_Template):

    def header_length(self):
        length = 0
        for field in self._fields:
            if not field.length.static:
                return length
            length += field.length.value
        return length

    def encode(self, message, header_params):
        header_params = header_params.copy()
        self._insert_length_to_header_parameters(header_params, message)
        header = MessageHeader(self.name)
        self._encode_fields(header, header_params)
        return header

    def _insert_length_to_header_parameters(self, header_params, message):
        pdu_field = self._get_pdu_field()
        pdu_length = len(message._raw)
        header_params[pdu_field.length.field] = pdu_field.length.solve_parameter(pdu_length)

    def _get_pdu_field(self):
        for field in self._fields:
            if field.type == 'pdu':
                return field
        return None

    # TODO: fields after the pdu
    def read(self, stream, timeout=None):
        data = stream.read(self.header_length(), timeout=timeout)
        data_index = 0
        field_index = 0
        header = MessageHeader(self.name)
        while len(data) > data_index:
            field = self._fields[field_index]
            header[field.name] = Field(field.type, field.name, data[data_index:data_index+field.length.value])
            data_index += field.length.value
            field_index +=1
        pdu_field = self._get_pdu_field()
        length_param = header[pdu_field.length.field].int
        pdu = stream.read(pdu_field.length.solve_value(length_param))
        return (header, pdu)

    def get_message_stream(self, buffered_stream):
        return MessageStream(buffered_stream, self)

class MessageTemplate(_Template):

    def __init__(self, message_name, protocol, header_params):
        _Template.__init__(self, message_name)
        self._protocol = protocol
        self.header_parameters = header_params

    def encode(self, message_params):
        message_params = message_params.copy()
        msg = Message(self.name)
        self._encode_fields(msg, message_params)
        if self._protocol:
            msg._add_header(self._protocol.encode(msg, self.header_parameters))
        return msg

    def decode(self, data):
        data_index = 0
        field_index = 0
        message = Message(self.name)
        while len(data) > data_index:
            field = self._fields[field_index]
            message[field.name] = Field(field.type, field.name, data[data_index:data_index+field.length.value])
            data_index += field.length.value
            field_index +=1
        return message

    def validate(self, message, message_fields):
        errors = []
        for field in self._fields:
            errors += field.validate(message[field.name].bytes, message_fields)
        return errors


class _TemplateField(object):

    def _get_element_value(self, paramdict):
        return paramdict.get(self.name, self.default_value)

    def _get_element_value_and_remove_from_params(self, paramdict):
        return paramdict.pop(self.name, self.default_value)

    def encode(self, paramdict):
        value = self._get_element_value_and_remove_from_params(paramdict)
        return self._encode_value(value)

    def validate(self, value, paramdict):
        forced_value = self._get_element_value(paramdict)
        if not forced_value or forced_value == 'None':
            return []
        if forced_value.startswith('('):
            return self._validate_pattern(forced_value, value)
        else:
            return self._validate_exact_match(forced_value, value)

    def _validate_pattern(self, forced_pattern, value):
        patterns = forced_pattern[1:-1].split('|')
        for pattern in patterns:
            if self._is_match(pattern, value):
                return []
        return ['Value of field %s does not match pattern %s!=%s' %
                (self.name, to_0xhex(value), forced_pattern)]

    def _is_match(self, forced_value, value):
        forced_binary_val = self._encode_value(forced_value)
        return forced_binary_val == value

    def _validate_exact_match(self, forced_value, value):
        if not self._is_match(forced_value, value):
            return ['Value of field %s does not match %s!=%s' %
                    (self.name, to_0xhex(value), forced_value)]
        return []


class UInt(_TemplateField):

    type = 'uint'

    def __init__(self, length, name, default_value=None):
        self.length = Length(length)
        self.name = name
        self.default_value = default_value if default_value and default_value != '""' else None

    def _encode_value(self, value):
        return to_bin_of_length(self.length.value, value)


class Char(_TemplateField):

    type = 'char'

    def __init__(self, length, name, default_value=None):
        self.length = Length(length)
        self.name = name
        self.default_value = default_value if default_value and default_value != '""' else None

    def _encode_value(self, value):
        return str(value.ljust(self.length.value, '\x00')) if value else ''


class PDU(object):

    type = 'pdu'

    def __init__(self, length):
        self.length = Length(length)

    def encode(self, params):
        return ''


def Length(value):
    if str(value).isdigit():
        return _StaticLength(int(value))
    return _DynamicLength(value)

# TODO: extend int
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


class MessageStream(object):

    def __init__(self, stream, protocol):
        self._cache = []
        self._stream = stream
        self._protocol = protocol

    def get(self, message_template, timeout=None):
        header_fields = message_template.header_parameters
        print "*TRACE* Get message with params %s" % header_fields
        msg = self._get_from_cache(message_template, header_fields)
        if msg:
            print "*TRACE* Cache hit. Cache currently has %s messages" % len(self._cache)
            return msg
        while True:
            header, pdu = self._protocol.read(self._stream, timeout=timeout)
            if self._matches(header, header_fields):
                return self._to_msg(message_template, header, pdu)
            else:
                self._cache.append((header, pdu))

    def _get_from_cache(self, template, fields):
        index = 0
        while index < len(self._cache):
            header, pdu = self._cache[index]
            if self._matches(header, fields):
                self._cache.pop(index)
                return self._to_msg(template, header, pdu)
        return None

    def _to_msg(self, template, header, pdu):
        msg = template.decode(pdu)
        msg._add_header(header)
        return msg

    def _matches(self, header, fields):
        for field in fields:
            if fields[field] and header[field].bytes  != to_bin(fields[field]):
                return False
        return True

    def empty(self):
        self.cache = []
        self._stream.empty()