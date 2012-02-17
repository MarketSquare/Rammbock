# API prototype
from Network import TCPServer, TCPClient, UDPServer, UDPClient, _NamedCache

from Protocol import Protocol, UInt, PDU, MessageTemplate, Char, Struct
from binary_conversions import to_0xhex, to_bin

# TODO: pass configuration parameters like timeout, name, and connection using caps and ':'
# example: TIMEOUT:12   CONNECTION:Alias
# This should make it easier to separate configs from message field arguments
class Rammbock(object):

    def __init__(self):
        self._init_caches()

    def _init_caches(self):
        self._protocol_in_progress = None
        self._protocols = {}
        self._servers = _NamedCache('server')
        self._clients = _NamedCache('client')
        self._message_stack = []

    def reset_rammbock(self):
        """Closes all connections, deletes all servers, clients, and protocols.

        You should call this method before exiting your test run. This will close all the connections and the ports
        will therefore be available for reuse faster.
        """
        for server in self._servers:
            server.close()
        for client in self._clients:
            client.close()
        self._init_caches()

    def start_protocol_description(self, protocol_name):
        """Start defining a new protocol template.

        All messages sent and received from a connection that uses a protocol have to conform to this protocol template.
        Protocol template fields can be used to search messages from buffer.
        """
        if self._protocol_in_progress:
            raise Exception('Can not start a new protocol definition in middle of old.')
        if protocol_name in self._protocols:
            raise Exception('Protocol %s already defined' % protocol_name)
        self._protocol_in_progress = Protocol(protocol_name)

    def end_protocol_description(self):
        """End protocol definition."""
        self._protocols[self._protocol_in_progress.name] = self._protocol_in_progress
        self._protocol_in_progress = None

    def start_udp_server(self, ip, port, name=None, timeout=None, protocol=None):
        protocol = self._get_protocol(protocol)
        server = UDPServer(ip=ip, port=port, timeout=timeout, protocol=protocol)
        return self._servers.add(server, name)

    def start_udp_client(self, ip=None, port=None, name=None, timeout=None, protocol=None):
        protocol = self._get_protocol(protocol)
        client = UDPClient(timeout=timeout, protocol=protocol)
        if ip or port:
            client.set_own_ip_and_port(ip=ip, port=port)
        return self._clients.add(client, name)

    def _get_protocol(self, protocol):
        protocol = self._protocols[protocol] if protocol else None
        return protocol

    def start_tcp_server(self, ip, port, name=None, timeout=None, protocol=None):
        protocol = self._get_protocol(protocol)
        server = TCPServer(ip=ip, port=port, timeout=timeout, protocol=protocol)
        return self._servers.add(server, name)

    def start_tcp_client(self, ip=None, port=None, name=None, timeout=None, protocol=None):
        protocol = self._get_protocol(protocol)
        client = TCPClient(timeout=timeout, protocol=protocol)
        if ip or port:
            client.set_own_ip_and_port(ip=ip, port=port)
        return self._clients.add(client, name)

    def get_client_protocol(self, name):
        return self._clients.get(name).protocol

    def accept_connection(self, name=None, alias=None):
        server = self._servers.get(name)
        server.accept_connection(alias)

    def connect(self, host, port, name=None):
        """Connect a client to certain host and port."""
        client = self._clients.get(name)
        client.connect_to(host, port)

    # TODO: Log the raw binary that is sent and received.
    def client_sends_binary(self, message, name=None):
        """Send raw binary data."""
        client = self._clients.get(name)
        client.send(message)

    # FIXME: support "send to" somehow. A new keyword?
    def server_sends_binary(self, message, name=None, connection=None):
        """Send raw binary data."""
        server = self._servers.get(name)
        server.send(message, alias=connection)

    def client_receives_binary(self, name=None, timeout=None):
        """Receive raw binary data."""
        client = self._clients.get(name)
        return client.receive(timeout=timeout)

    def server_receives_binary(self, name=None, timeout=None, connection=None):
        """Receive raw binary data."""
        return self.server_receives_binary_from(name, timeout, connection)[0]

    def server_receives_binary_from(self, name=None, timeout=None, connection=None):
        """Receive raw binary data. Returns message, ip, port"""
        server = self._servers.get(name)
        return server.receive_from(timeout=timeout, alias=connection)

    def new_message(self, message_name, protocol=None, *parameters):
        """Define a new message template.
    
        Parameters have to be header fields."""
        if self._protocol_in_progress:
            raise Exception("Protocol definition in progress. Please finish it before starting to define a message.")
        proto = self._get_protocol(protocol)
        _, header_fields = self._parse_parameters(parameters)
        self._message_stack.append(MessageTemplate(message_name, proto, header_fields))
        self._default_values = {}

    def get_message(self, *parameters):
        """Get encoded message.

        * Send Message -keywords are convenience methods, that will call this to get the message object and then send it.
        Parameters have to be pdu fields."""
        _, message_fields = self._parse_parameters(parameters)
        return self._encode_message(message_fields)

    def _encode_message(self, message_fields):
        msg = self._get_message_template().encode(message_fields)
        self._message_stack = []
        print '*DEBUG* %s' % repr(msg)
        return msg

    def _get_message_template(self):
        if len(self._message_stack) != 1:
            raise Exception('Message definition not complete.')
        return self._message_stack[0]

    def client_sends_message(self, *parameters):
        """Send a message.
    
        Parameters have to be message fields."""
        configs, message_fields = self._get_paramaters_with_defaults(parameters)
        msg = self._encode_message(message_fields)
        self.client_sends_binary(msg._raw, **configs)

    # FIXME: support "send to" somehow. A new keyword?
    def server_sends_message(self, *parameters):
        """Send a message.
    
        Parameters have to be message fields."""
        configs, message_fields = self._parse_parameters(parameters)
        msg = self._encode_message(message_fields)
        self.server_sends_binary(msg._raw, **configs)

    def client_receives_message(self, *parameters):
        """Receive a message object.
    
        Parameters that have been given are validated against message fields."""
        configs, message_fields = self._parse_parameters(parameters)
        client = self._clients.get(configs.get('name'))
        return client.get_message(self._get_message_template(), message_fields, **configs)

    def server_receives_message(self, *parameters):
        """Receive a message object.
    
        Parameters that have been given are validated against message fields."""
        configs, message_fields = self._get_paramaters_with_defaults(parameters)
        server = self._servers.get(configs.get('name'))
        return server.get_message(self._get_message_template(), message_fields, **configs)

    # TODO: character types
    # TODO: byte alignment support

    def uint(self, length, name, value=None):
        self._add_field(UInt(length, name, value))

    def char(self, length, name, value=None):
        self._add_field(Char(length, name, value))

    def _add_field(self, field):
        if self._protocol_in_progress:
            self._protocol_in_progress.add(field)
        else:
            self._message_stack[-1].add(field)

    def struct(self, type, name):
        self._message_stack.append(Struct(type, name))

    def end_struct(self):
        struct = self._message_stack.pop()
        self._add_field(struct)

    def pdu(self, length):
        """Defines the message in protocol template.

        Length must be the name of a previous field in template definition."""
        self._add_field(PDU(length))

    def hex_to_bin(self, hex_value):
        return to_bin(hex_value)

    def bin_to_hex(self, bin_value):
        return to_0xhex(bin_value)
    
    def _get_paramaters_with_defaults(self, parameters):
        config, fields = self._parse_parameters(parameters)
        self._populate_defaults(fields)
        return config, fields
    
    def _populate_defaults(self, fields):
        for key in iter(self._default_values):
            if not fields.has_key(key):
                fields[key] = self._default_values[key]
        self._default_values = {}
    
    def value(self, name, value):
        self._default_values[name] = value

    def _parse_parameters(self, parameters):
        configs, fields = {}, {}
        for parameter in parameters:
            self._parse_entry(parameter, configs, fields)
        return configs, fields

    def _parse_entry(self, param, configs, fields):
        colon_index = param.find(':')
        equals_index = param.find('=')
        # TODO: Cleanup. There must be a cleaner way.
        # Luckily test_rammbock.py has unit tests covering all paths.
        if colon_index==-1 and equals_index==-1:
            raise Exception('Illegal parameter %s' % param)
        elif equals_index==-1:
            self._set_name_and_value(fields, ':', param)
        elif colon_index==-1:
            self._set_name_and_value(configs, '=', param)
        elif colon_index>equals_index:
            self._set_name_and_value(configs, '=', param)
        else:
            self._set_name_and_value(fields, ':', param)

    def _set_name_and_value(self, dictionary, separator, parameter):
        index = parameter.find(separator)
        dictionary[parameter[:index].strip()] = parameter[index + 1:].strip()

    def _log_msg(self, loglevel, log_msg):
        print '*%s* %s' % (loglevel, log_msg)

