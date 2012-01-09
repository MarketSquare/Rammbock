# API prototype

from struct import Struct
from Network import UDPServer, UDPClient, _NamedCache

class Rammbock(object):

    def __init__(self):
        self._current_protocol = None
        self._protocols = {}
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
        self._current_protocol.parse_protocol_header()
        self._current_protocol = None

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
    def send_binary(self, message, _server=None, _client=None, *params):
        raise Exception('Not yet done')

    """Receive raw binary data."""
    def receive_binary(self, _server=None, _client=None, *params):
        raise Exception('Not yet done')

    """Define a new message pdu template.

    Parameters have to be header fields."""
    def new_pdu(self, *params):
        self._current_protocol.reset_message()

    """Send a pdu.

    Parameters have to be pdu fields."""
    def send_pdu(self, *params):
        raise Exception('Not yet done')

    """Receive a message object.

    Parameters that have been given are validated against message fields."""
    def receive_pdu(self, *params):
        raise Exception('Not yet done')

    def add_number(self, length, name, value):
        self._current_protocol.add(_UField(length, name, value))

    def u8(self, name, default_value=None):
        self.add_number(1, name, default_value)

    def u16(self, name, default_value=None):
        self.add_number(2, name, default_value)

    def u32(self, name, default_value=None):
        self.add_number(4, name, default_value)

    """Defines the pdu in protocol template.

    Length must be the name of a previous field in template definition."""
    def pdu(self, length):
        self._current_protocol.add(_PDUField(length))

    def hex_to_bin(self, hex_value):
        raise Exception('Not yet done')


class Protocol(object):

    def __init__(self):
        self.ready = False
        self._protocol_template = _Template()
        self._message_template = None
        self.header_format = None

    def add(self, field):
        self._add_to_protocol_template(field) if not self.ready else self._add_to_message_template(field)

    def reset_message(self):
        self._message_template = _Template()

    def _add_to_protocol_template(self, field):
        self._protocol_template.add(field)

    def _add_to_message_template(self, field):
        self._message_template.add(field)

    def parse_protocol_header(self):
        self.header_format = Struct("".join(str(x.length) + x.struct_code for x in self._protocol_template.fields if x.struct_code != 'N/A'))

class _Template(object):

    def __init__(self):
        self.fields = []

    def add(self, to_add):
        self.fields.append(to_add)


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
        forced_binary_val = to_bin_of_length(length, forced_value)
        return forced_binary_val == value

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

class _PDUField(object):

    struct_code = 'N/A'

    def __init__(self, length):
        self.length = length

