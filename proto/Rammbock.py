# API prototype

from struct import Struct
from Network import UDPServer, UDPClient, _NamedCache
from binary_conversions import to_0xhex, to_bin, to_bin_of_length, to_hex

class Rammbock(object):

    def __init__(self):
        self._current_protocol = None
        self._protocols = {}
        self._message_pdu = None
        self._default_client = None
        self._default_server = None
        self._servers = _NamedCache('server')
        self._clients = _NamedCache('clients')

    """Start defining a new protocol template.

    All messages sent and received from a connection after calling 'Use protocol' have to use the same protocol template. Protocol template fields can be used to search messages from buffer.
    """
    def start_protocol_description(self, protocol):
        self._protocols[protocol] = Protocol()
        self._current_protocol = self._protocols[protocol]

    """End protocol definition."""
    def end_protocol_description(self):
        self._current_protocol.ready = True

    def start_udp_server(self, ip, port, name=None, timeout=None):
        server = UDPServer(ip, port, timeout)
        self._servers.add(server, name)
        return server

    def start_udp_client(self, ip=None, port=None, _client=None):
        client = UDPClient()
        self._clients.add(client, _client)
        return client

    """Connect a client to certain host and port."""
    def connect(self, host, port, _client=None):
        client = self._clients.get(_client) if _client else self._clients.get()
        client.connect_to(host, port)

    """Take a certain protocol into use in server or client.

    From this moment on (until another protocol is taken into use) all messages received and sent have to confirm to this protocol template."""
    def use_protocol(self, protocol, _server=None, _client=None):
        self._current_protocol = self._protocols[protocol]
        self._default_client = _client
        self._default_server = _server

    """Send raw binary data."""
    def send_binary(self, message, _server=None, _client=None):
        server = _server if _server else self._default_server
        client = _client if _client else self._default_client
        client.send(message)

    """Receive raw binary data."""
    def receive_binary(self, _server=None, _client=None):
        raise Exception('Not yet done')

    """Define a new message pdu template.

    Parameters have to be header fields."""
    def new_pdu(self, *parameters):
        self._message_pdu = PDU(self._parse_parameters(parameters))

    """Send a pdu.

    Parameters have to be pdu fields."""
    def send_pdu(self, *params):
        paramsdict = self._parse_parameters(params)
        server = paramsdict.pop("_server", self._default_server)
        client = paramsdict.pop("_client", self._default_client)
        msg = self.create_binary_to_send(paramsdict)
        self.send_binary(msg, server, client)

    def create_binary_to_send(self, paramsdict):
        msg = self._current_protocol.encode(self._message_pdu, paramsdict)
        self._log_msg('DEBUG', repr(msg))
        return msg._raw

    """Receive a message object.

    Parameters that have been given are validated against message fields."""
    def receive_pdu(self, *params):
        raise Exception('Not yet done')

    def add_number(self, length, name, value):
        field = _UField(length, name, value)
        if self._message_pdu:
            self._message_pdu.add(field)
        elif not self._current_protocol.ready:
            self._current_protocol.add(field)
        else:
            raise Exception('Fields have to be added in protocol definition or in message template.')

    def u8(self, name, default_value=None):
        self.add_number(1, name, default_value)

    def u16(self, name, default_value=None):
        self.add_number(2, name, default_value)

    def u32(self, name, default_value=None):
        self.add_number(4, name, default_value)

    """Defines the pdu in protocol template.

    Length must be the name of a previous field in template definition."""
    def pdu(self, length):
        self._current_protocol.add(_PDUField(0, "pdu", "placeholder"))

    def hex_to_bin(self, hex_value):
        return to_bin(hex_value)

    def _parse_parameters(self, parameters):
        result = {}
        for parameter in parameters:
            index = parameter.find('=')
            result[parameter[:index].strip()] = parameter[index + 1:].strip()
        return result


class Protocol(object):

    def __init__(self):
        self.ready = False
        self._header_fields = []
        self._header_format = None
        self._parameters = None

    def add(self, field):
        if self.ready:
            raise Exception('Protocol already defined')
        self._add_to_protocol_template(field) 

    def reset_message(self):
        self._message_fields = []

    def encode(self, pdu, pdu_parameters):
        header_params = pdu.get_header_params()
        self._verify_params_in_header(header_params)
        encoded_pdu = pdu.encode(pdu_parameters)
        msg = _EncodedMsg('TODO: name', encoded_pdu)
        for field in self._header_fields:
            msg[field.name] = field.encode_field(header_params)
        return msg

    def _verify_params_in_header(self, paramdict):
        params = set(paramdict.keys())
        if not params.issubset(set([field.name for field in self._header_fields])):
            raise AssertionError("Message does not have field(s) %s." % (' '.join(params.difference(self._header_fields))))

    def _add_to_protocol_template(self, field):
        self._header_fields.append(field)


class PDU(object):

    def __init__(self, header_parameters):
        self._fields = []
        self._header_parameters = header_parameters

    def add(self, field):
        self._fields.append(field)

    def get_header_params(self):
        return self._header_parameters

    def encode(self, pdu_params):
        msg = _EncodedPDU()
        for field in self._fields:
            msg[field.name] = field.encode_field(pdu_params)
        return msg


class _TemplateField(object):

    def __init__(self, length, name, value):
        self.name = name
        self.length = int(length)
        self.set_value(value)

    def set_value(self, value):
        self.value = value

    def receive_field_and_validate(self, value, paramdict, big_endian=True):
        field = self._receive_field(value, big_endian)
        errors = self._validate(field, paramdict)
        return field, errors

    def encode_field(self, paramdict):
        value = self._get_element_value(paramdict)
        if value is None:
            raise Exception('Value of %s is not set.' % self.name)
        return self._encode_binary_value(value)

    def _receive_field(self, value, big_endian):
        return value

    def _get_element_value(self, paramdict):
        return paramdict.get(self.name, self.value)

    def _validate(self, value, paramdict):
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
            if self._is_match(self.name, self.length, pattern, value):
                return []
        return ['Value of element %s does not match pattern %s!=%s' %
                (self.name, to_hex(value), forced_pattern)]

    def _is_match(self, name, length, forced_value, value):
        expected_binary_val = to_bin_of_length(length, forced_value)
        return expected_binary_val == value

    def _validate_exact_match(self, forced_value, value):
        if not self._is_match(self.name, self.length, forced_value, value):
            return ['Value of element %s does not match %s!=%s' %
                    (self.name, to_hex(value), forced_value)]
        return []


class _UField(_TemplateField):

    struct_code = 'c'

    def _receive_field(self, value, big_endian):
        return self._convert_value_byte_order(value, big_endian)

    def _convert_value_byte_order(self, value, big_endian):
        return value if big_endian else value[::-1]

    def _encode_binary_value(self, value):
        return to_bin_of_length(self.length, value)


class _StringField(_TemplateField):

    struct_code = 's'

    def _encode_binary_value(self, value):
        return value.ljust(self.length, '\x00')


class _PDUField(_TemplateField):

    struct_code = 'N/A'

    def __init__(self, length, name, value):
        self.name = name
        self.length_field_name = length
        self.set_value(value)


class _Encoded(object):

    def __init__(self):
        self.__fields = []

    def __setitem__(self, name, value):
        self.__fields.append(_EncodedField(name, value))

    def __getitem__(self, name):
        for field in self.__fields:
            if field.name == name:
                return field
        raise KeyError(name)

    def __getattr__(self, name):
        return self[name]

    def __raw(self):
        return ''.join([field.bytes for field in self.__fields])


class _EncodedPDU(_Encoded):

    def __str__(self):
        result = ''
        for field in self.__fields:
            result +='  %s\n' % repr(field)
        return result

    @property
    def _raw(self):
        return self.__raw()


class _EncodedMsg(_Encoded):

    def __init__(self, name, pdu):
        self.__name = name
        self.__pdu = pdu
        _Encoded.__init__(self)

    def __str__(self):
        return 'Message %s' % self.__name

    def __repr__(self):
        result = 'Message %s header: %s \n' % (self.__name, ' '.join([repr(field for field in self.__fields)]))
        result += str(self.__pdu)
        return result

    @property
    def _raw(self):
        return self.__header._raw + self.__raw()


class _EncodedField(object):

    def __init__(self, name, value):
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

    def __str__(self):
        return self.hex

    def __repr__(self):
        return '%s = %s' % (self.name, str(self))
