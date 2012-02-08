# API prototype
import time
from Network import TCPServer
from Network import TCPClient

from Network import UDPServer, UDPClient, _NamedCache
from binary_conversions import to_0xhex, to_bin, to_bin_of_length, to_hex

class Rammbock(object):

    def __init__(self):
        self._protocols = _NamedCache('protocol')
        self._servers = _NamedCache('server')
        self._clients = _NamedCache('client')

    def reset_rammbock(self):
        """

        Closes all connections, deletes all servers and clients, templates and messages
        """
        raise Exception('NYI')

    def start_protocol_description(self, protocol):
        """Start defining a new protocol template.

        All messages sent and received from a connection after calling 'Use protocol' have to use the same protocol template. Protocol template fields can be used to search messages from buffer.
        """
        raise Exception('NYI')

    def end_protocol_description(self):
        """End protocol definition."""
        raise Exception('NYI')

    def start_udp_server(self, _ip, _port, _name=None, _timeout=None, _protocol=None):
        raise Exception('NYI')

    def start_udp_client(self, _ip=None, _port=None, _name=None, _timeout=None, _protocol=None):
        raise Exception('NYI')

    def start_tcp_server(self, _ip, _port, _name=None, _timeout=None, _protocol=None):
        server = TCPServer(ip=_ip, port=_port, timeout=_timeout, protocol=_protocol)
        self._servers.add(server, _name)

    def start_tcp_client(self, _ip=None, _port=None, _name=None, _timeout=None, _protocol=None):
        client = TCPClient(timeout=_timeout, protocol=_protocol)
        if _ip or _port:
            client.set_own_ip_and_port(ip=_ip, port=_port)

    def accept_connection(self, _name=None, _alias=None):
        raise Exception('NYI')

    def connect(self, host, port, _client=None):
        """Connect a client to certain host and port."""
        raise Exception('NYI')

    def client_sends_binary(self, message, _name=None):
        """Send raw binary data."""
        raise Exception('NYI')

    def server_sends_binary(self, message, _name=None, _connection=None):
        """Send raw binary data."""
        raise Exception('NYI')

    def client_receives_binary(self, _name=None, _timeout=None):
        """Receive raw binary data."""
        raise Exception('NYI')

    def server_receives_binary(self, _name=None, _timeout=None, _connection=None):
        """Receive raw binary data."""
        raise Exception('NYI')

    def new_message(self, protocol=None, *parameters):
        """Define a new message pdu template.
    
        Parameters have to be header fields."""
        raise Exception('NYI')

    def get_message(self, *params):
        """Get encoded message.
    
        Parameters have to be pdu fields."""
        raise Exception('NYI')

    def client_sends_message(self, *params):
        """Send a pdu.
    
        Parameters have to be pdu fields."""
        raise Exception('NYI')

    def server_sends_message(self, *params):
        """Send a pdu.
    
        Parameters have to be pdu fields."""
        raise Exception('NYI')

    def client_receives_message(self, *params):
        """Receive a message object.
    
        Parameters that have been given are validated against message fields."""
        raise Exception('Not yet done')

    def server_receives_message(self, *params):
        """Receive a message object.
    
        Parameters that have been given are validated against message fields."""
        raise Exception('Not yet done')

    def uint(self, length, name, value):
        raise Exception('NYI')

    def pdu(self, length):
        """Defines the pdu in protocol template.

        Length must be the name of a previous field in template definition."""
        raise Exception('Not yet done')

    def hex_to_bin(self, hex_value):
        return to_bin(hex_value)

    def bin_to_hex(self, bin_value):
        return to_0xhex(bin_value)

    def _parse_parameters(self, parameters):
        result = {}
        for parameter in parameters:
            index = parameter.find('=')
            result[parameter[:index].strip()] = parameter[index + 1:].strip()
        return result

    def _log_msg(self, loglevel, log_msg):
        print '*%s* %s' % (loglevel, log_msg)


class Protocol(object):

    def __init__(self):
        self.ready = False
        self._header_fields = []
        self._header_format = None
        self._parameters = None
        self._pdu_length_field = None

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
        header_params[self._pdu_length_field] = len(encoded_pdu._raw) + self._pdu_length_minus
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
        if field.pdu_field:
            self._pdu_length_field, self._pdu_length_minus = field.length_field_name, field.length_minus

    def receive(self, connection, paramdict):
        # FIXME: build a support for a message stream tokenized by the protocol
        timeout = float(paramdict.get('_timeout', self._default_timeout))
        cutoff = time.time() + timeout
        while time.time() < cutoff:
            bytes = connection.read()
            raise Exception('Not ready')

    def _receive_fields(self, bytes, paramdict):
        msg = _EncodedMsg('TODO: name', None)
        i = 0
        errors_list = []
        for field in self._header_fields:
            # FIXME: handle the length field as a special case...
            value = bytes[i:i + field.length]
            msg[field.name], errors = field.receive_field_and_validate(value, paramdict)
            errors_list.extend(errors)
            i += field.length
        if i != len(bytes):
            errors_list.append('Error in response %s. Length did not match expected. Expected length %d, received %d' %
                               (self.name, i, len(bytes)))
        return msg, errors_list

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

    pdu_field = False

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

    pdu_field = True

    def __init__(self, length, name, value):
        self.name = name
        self.length_field_name, self.length_minus = self._parse_length_field(length)
        self.set_value(value)

    # TODO: major rework needed
    def _parse_length_field(self, length):
        field,minus = length.split('-')
        return field.strip(), int(minus)

    def _encode_binary_value(self, value):
        return ''

    def receive_field_and_validate(self, value, paramdict, big_endian=True):
        raise Exception('Not ready yet, sh')


class _Encoded(object):

    def __init__(self):
        self._fields = []

    def __setitem__(self, name, value):
        self._fields.append(_EncodedField(name, value))

    def __getitem__(self, name):
        for field in self._fields:
            if field.name == name:
                return field
        raise KeyError(name)

    def __getattr__(self, name):
        return self[name]

    def _get_raw(self):
        return ''.join([field.bytes for field in self._fields])


class _EncodedPDU(_Encoded):

    def __str__(self):
        result = ''
        for field in self._fields:
            result +='  %s\n' % repr(field)
        return result

    @property
    def _raw(self):
        return self._get_raw()


class _EncodedMsg(_Encoded):

    def __init__(self, name, pdu):
        self.__name = name
        self.__pdu = pdu
        _Encoded.__init__(self)

    def __str__(self):
        return 'Message %s' % self.__name

    def __repr__(self):
        result = 'Message %s header: %s \n' % (self.__name, ' '.join([repr(field for field in self._fields)]))
        result += str(self.__pdu)
        return result

    @property
    def _raw(self):
        return self._get_raw() + self.__pdu._raw


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
