from Message import Field, Message, MessageHeader, _MessageStruct
from message_stream import MessageStream
from primitives import Length
import re

class _Template(object):

    def __init__(self, name):
        self._fields = []
        self.name = name

    def add(self, field):
        if field.has_length and not field.length.static:
            if not field.length.field in [elem.name for elem in self._fields]:
                raise Exception('Length field %s unknown' % field.length)
        self._fields.append(field)

    def _encode_fields(self, struct, params):
        for field in self._fields:
            # TODO: clean away this ugly hack that makes it possible to skip PDU
            # (now it is a 0 length place holder in header)
            encoded = field.encode(params, struct)
            if encoded:
                struct[field.name] = encoded
        if params:
            raise Exception('Unknown fields in header %s' % str(params))

    def decode(self, data, parent=None, name=None):
        message = self._get_struct(name)
        data_index = 0
        for field in self._fields:
            message[field.name] = field.decode(data[data_index:], message)
            data_index += len(message[field.name])
        return message


    def validate(self, message, message_fields):
        errors = []
        for field in self._fields:
            errors += field.validate(message, message_fields)
        return errors


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
        pdu = stream.read(pdu_field.length.calc_value(length_param))
        return (header, pdu)

    def get_message_stream(self, buffered_stream):
        return MessageStream(buffered_stream, self)

class MessageTemplate(_Template):
    
    type = 'Message'

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

    def _get_struct(self, name):
        return Message(self.name)

class Struct(_Template):

    has_length = False
    
    def __init__(self, type, name):
        self.type = type
        _Template.__init__(self,name)

    def encode(self, message_params, parent, name=None):
        struct = _MessageStruct(name if name else self.name)
        self._encode_fields(struct, self._get_params_sub_tree(message_params, name))
        return struct

    def _get_struct(self, name):
        return _MessageStruct(name if name else self.name)

    def _get_params_sub_tree(self, params, name=None):
        result = {}
        name = name if name else self.name
        for key in params.keys():
            prefix, _, ending = key.partition('.')
            if prefix == name:
                result[ending] = params.pop(key)
        return result

    def validate(self, parent, message_fields, name=None):
        name = name if name else self.name
        message = parent[name]
        return _Template.validate(self, message, self._get_params_sub_tree(message_fields, name))

class List(_Template):

    param_pattern = re.compile(r'(.*?)\[(.*?)\](.*)')

    has_length = True
    
    type = 'List'
    def __init__(self, length, name):
        self.length = Length(length)
        _Template.__init__(self,name)

    def encode(self, message_params, parent, name=None):
        name = name if name else self.name
        params_subtree = self._get_params_sub_tree(message_params, name)
        list = self._get_struct(name)
        for index in range(0, self.length.decode(parent)):
            list[str(index)] = self.field.encode(params_subtree, parent, name=str(index))
        if params_subtree:
            raise Exception('Unknown fields in %s %s' % (name, str(params_subtree)))
        return list

    @property
    def field(self):
        return self._fields[0]

    def _get_struct(self, name=None):
        return _MessageStruct("%s %s" % (name if name else self.name, self.field.type))

    def decode(self, data, parent, name=None):
        name = name if name else self.name
        message = self._get_struct(name)
        data_index = 0
        for index in range(0,self.length.decode(parent)):
            message[str(index)] = self.field.decode(data[data_index:], message, name=str(index))
            data_index += len(message[index])
        return message

    def validate(self, parent, message_fields, name=None):
        name = name if name else self.name
        params_subtree = self._get_params_sub_tree(message_fields, name)
        list = parent[name]
        errors = []
        for index in range(0,self.length.decode(parent)):
            errors += self.field.validate(list, params_subtree, name=str(index))
        return errors

    def _get_params_sub_tree(self, params, name=None):
        result = {}
        name = name if name else self.name
        for key in params.keys():
            match = self.param_pattern.match(key)
            if match:        
                prefix, child_name, ending = match.groups()
                if prefix == name:
                    result[child_name + ending] =  params.pop(key)
        return result

