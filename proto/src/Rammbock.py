from __future__ import with_statement
from contextlib import contextmanager
from Networking import TCPServer, TCPClient, UDPServer, UDPClient, _NamedCache
from message_sequence import MessageSequence
from templates import Protocol, UInt, PDU, MessageTemplate, Char, Binary, \
    StructTemplate, ListTemplate, UnionTemplate, BinaryContainerTemplate
from binary_tools import to_0xhex, to_bin
from templates.containers import TBCDContainerTemplate
from templates.primitives import TBCD


class Rammbock(object):

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        self._init_caches()

    def _init_caches(self):
        self._protocol_in_progress = None
        self._protocols = {}
        self._servers = _NamedCache('server')
        self._clients = _NamedCache('client')
        self._message_stack = []
        self._field_values = None
        self._message_sequence = MessageSequence()

    @property
    def _current_container(self):
        return self._message_stack[-1]

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

    def reset_message_streams(self):
        """ Resets streams of incoming messages.
        
        You can use this method to reuse the same connections for several consecutive test cases.
        """
        for client in self._clients:
            client.empty()
        for server in self._servers:
            server.empty()

    def start_protocol_description(self, protocol_name):
        """Start defining a new protocol template.

        All messages sent and received from a connection that uses a protocol have to conform to this protocol template.
        """
        if self._protocol_in_progress:
            raise Exception('Can not start a new protocol definition in middle of old.')
        if protocol_name in self._protocols:
            raise Exception('Protocol %s already defined' % protocol_name)
        self._protocol_in_progress = Protocol(protocol_name)

    def end_protocol_description(self):
        """End protocol definition."""
        self._protocol_in_progress.verify()
        self._protocols[self._protocol_in_progress.name] = self._protocol_in_progress
        self._protocol_in_progress = None

    def start_udp_server(self, ip, port, name=None, timeout=None, protocol=None):
        """Starts a new UDP server to given `ip` and `port`.

        Server can be given a `name`, default `timeout` and a `protocol`.
        """
        self._start_server(UDPServer, ip, port, name, timeout, protocol)

    def start_tcp_server(self, ip, port, name=None, timeout=None, protocol=None):
        """Starts a new TCP server to given `ip` and `port`.

        Server can be given a `name`, default `timeout` and a `protocol`. Notice that you have to use
        `Accept Connection` keyword for server to receive connections.
        """
        self._start_server(TCPServer, ip, port, name, timeout, protocol)

    def _start_server(self, server_class, ip, port, name=None, timeout=None, protocol=None):
        protocol = self._get_protocol(protocol)
        server = server_class(ip=ip, port=port, timeout=timeout, protocol=protocol)
        return self._servers.add(server, name)

    def start_udp_client(self, ip=None, port=None, name=None, timeout=None, protocol=None):
        """Starts a new UDP client.

        Client can be optionally given `ip` and `port` to bind to, as well as `name`, default `timeout` and a `protocol`.
        You should use `Connect` keyword to connect client to a host.
        """
        self._start_client(UDPClient, ip, port, name, timeout, protocol)

    def start_tcp_client(self, ip=None, port=None, name=None, timeout=None, protocol=None):
        """Starts a new TCP client.

        Client can be optionally given `ip` and `port` to bind to, as well as `name`, default `timeout` and a `protocol`.
        You should use `Connect` keyword to connect client to a host.
        """
        self._start_client(TCPClient, ip, port, name, timeout, protocol)

    def _start_client(self, client_class, ip=None, port=None, name=None, timeout=None, protocol=None):
        protocol = self._get_protocol(protocol)
        client = client_class(timeout=timeout, protocol=protocol)
        if ip or port:
            client.set_own_ip_and_port(ip=ip, port=port)
        return self._clients.add(client, name)

    def _get_protocol(self, protocol):
        protocol = self._protocols[protocol] if protocol else None
        return protocol

    def get_client_protocol(self, name=None):
        """Returns name of the protocol client uses or empty if client does not use a protocol.
        """
        return self._clients.get(name).protocol_name or ''

    def accept_connection(self, name=None, alias=None):
        """Accepts a connection to server identified by `name` or the latest server if `name` is empty.

        If given an `alias`, the connection is named and can be later referenced with that name.
        """
        server = self._servers.get(name)
        server.accept_connection(alias)

    def connect(self, host, port, name=None):
        """Connects a client to given `host` and `port`. If client `name` is not given then connects the latest client."""
        client = self._clients.get(name)
        client.connect_to(host, port)

    def _register_send(self, sender, label, name, connection=None):
        self._message_sequence.send(name, sender.get_own_address(), sender.get_peer_address(alias=connection),
                                    sender.protocol_name, label)

    def _register_receive(self, receiver, label, name, error='', connection=None):
        self._message_sequence.receive(name, receiver.get_own_address(), receiver.get_peer_address(alias=connection),
                                       receiver.protocol_name, label, error)

    def client_sends_binary(self, message, name=None, label=None):
        """Send raw binary `message`.

        If client `name` is not given, uses the latest client. Optional message `label` is shown on logs."""
        client, name = self._clients.get_with_name(name)
        client.send(message)
        self._register_send(client, label, name)

    # FIXME: support "send to" somehow. A new keyword?
    def server_sends_binary(self, message, name=None, connection=None, label=None):
        """Send raw binary `message`.

        If server `name` is not given, uses the latest server. Optional message `label` is shown on logs."""
        server, name = self._servers.get_with_name(name)
        server.send(message, alias=connection)
        self._register_send(server, label, name, connection=connection)

    def client_receives_binary(self, name=None, timeout=None, label=None):
        """Receive raw binary message.

        If client `name` is not given, uses the latest client. Optional message `label` is shown on logs."""
        client, name = self._clients.get_with_name(name)
        msg = client.receive(timeout=timeout)
        self._register_receive(client, label, name)
        return msg

    def server_receives_binary(self, name=None, timeout=None, connection=None, label=None):
        """Receive raw binary message.

        If server `name` is not given, uses the latest server. Optional message `label` is shown on logs."""
        return self.server_receives_binary_from(name, timeout, connection=connection)[0]

    def server_receives_binary_from(self, name=None, timeout=None, connection=None, label=None):
        """Receive raw binary message. Returns message, ip, and port

        If server `name` is not given, uses the latest server. Optional message `label` is shown on logs."""
        server, name = self._servers.get_with_name(name)
        msg, ip, port = server.receive_from(timeout=timeout, alias=connection)
        self._register_receive(server, label, name, connection=connection)
        return msg, ip, port

    def new_message(self, message_name, protocol=None, *parameters):
        """Define a new message template with `message_name`.

        `protocol` has to be defined earlier with `Start Protocol Description`. Optional parameters are
        default values for message header separated with colon."""
        if self._protocol_in_progress:
            raise Exception("Protocol definition in progress. Please finish it before starting to define a message.")
        proto = self._get_protocol(protocol)
        _, header_fields, _ = self._parse_parameters(parameters)
        self._message_stack = [MessageTemplate(message_name, proto, header_fields)]
        self._field_values = {}

    def get_message(self, *parameters):
        """Get encoded message.

        * Send Message -keywords are convenience methods, that will call this to get the message object and then send it.
        Optional parameters are message field values separated with colon."""
        _, message_fields, header_fields = self._get_parameters_with_defaults(parameters)
        return self._encode_message(message_fields, header_fields)

    def _encode_message(self, message_fields, header_fields):
        msg = self._get_message_template().encode(message_fields, header_fields)
        print '*DEBUG* %s' % repr(msg)
        return msg

    def _get_message_template(self):
        if len(self._message_stack) != 1:
            raise Exception('Message definition not complete. %s not completed.' % self._current_container.name)
        return self._message_stack[0]

    def client_sends_message(self, *parameters):
        """Send a message defined with `New Message`.

        Optional parameters are client `name` separated with equals and message field values separated with colon.
        Protocol header values can be set with syntax header:header_field_name:value."""
        self._send_message(self.client_sends_binary, parameters)

    # FIXME: support "send to" somehow. A new keyword?
    def server_sends_message(self, *parameters):
        """Send a message defined with `New Message`.

        Optional parameters are server `name` and possible connection `alias` separated with equals and message field
        values separated with colon. Protocol header values can be set with syntax header:header_field_name:value."""
        self._send_message(self.server_sends_binary, parameters)

    def _send_message(self, callback, parameters):
        configs, message_fields, header_fields = self._get_parameters_with_defaults(parameters)
        msg = self._encode_message(message_fields, header_fields)
        callback(msg._raw, label=self._current_container.name, **configs)

    def client_receives_message(self, *parameters):
        """Receive a message with template defined using `New Message` and validate field values.

        Message template has to be defined with `New Message` before calling this. Optional parameters are client `name`
        and possible `timeout` separated with equals and message field values for validation separated with colon."""
        with self._receive(self._clients, *parameters) as (msg, message_fields):
            self._validate_message(msg, message_fields)
            return msg

    def client_receives_without_validation(self, *parameters):
        """Receive a message with template defined using `New Message`.

        Message template has to be defined with `New Message` before calling this. Optional parameters are client `name`
        and possible `timeout` separated with equals and message field values for validation separated with colon."""
        with self._receive(self._clients, *parameters) as (msg, _):
            return msg

    def server_receives_message(self, *parameters):
        """Receive a message with template defined using `New Message` and validate field values.

        Message template has to be defined with `New Message` before calling this. Optional parameters are server `name`
        and possible `timeout` separated with equals and message field values for validation separated with colon."""
        with self._receive(self._servers, *parameters) as (msg, message_fields):
            self._validate_message(msg, message_fields)
            return msg

    def server_receives_without_validation(self, *parameters):
        """Receive a message with template defined using `New Message`.

        Message template has to be defined with `New Message` before calling this. Optional parameters are server `name`
        and possible `timeout` separated with equals and message field values for validation separated with colon."""
        with self._receive(self._servers, *parameters) as (msg, _):
            return msg

    def validate_message(self, msg, *parameters):
        """Validates given message using template defined with `New Message` and field values given as optional arguments.
        """
        _, message_fields, _ = self._get_parameters_with_defaults(parameters)
        self._validate_message(msg, message_fields)

    def _validate_message(self, msg, message_fields):
        errors = self._get_message_template().validate(msg, message_fields)
        if errors:
            print "Validation failed for %s" % repr(msg)
            print '\n'.join(errors)
            raise AssertionError(errors[0])

    @contextmanager
    def _receive(self, nodes, *parameters):
        configs, message_fields, _ = self._get_parameters_with_defaults(parameters)
        node, name = nodes.get_with_name(configs.pop('name', None))
        msg = node.get_message(self._get_message_template(), **configs)
        try:
            yield msg, message_fields
            self._register_receive(node, self._current_container.name, name)
            print "*DEBUG* Received %s" % repr(msg)
        except AssertionError, e:
            self._register_receive(node, self._current_container.name, name, error=e.args[0])
            raise e


    def uint(self, length, name, value=None, align=None):
        """Add an unsigned integer to template.

        `length` is given in bytes and `value` is optional. `align` can be used to align the field to longer byte length.
        """
        self._add_field(UInt(length, name, value, align=align))

    def chars(self, length, name, value=None):
        """Add a char array to template.

        `length` is given in bytes and can refer to earlier numeric fields in template. `value` is optional.
        """

        self._add_field(Char(length, name, value))

    def _add_field(self, field):
        if self._protocol_in_progress:
            self._protocol_in_progress.add(field)
        else:
            self._current_container.add(field)

    def struct(self, type, name, *parameters):
        """Defines a new struct to template.

        You must call `End Struct` to end struct definition. `type` is the name for generic type and `name` is the field
        name in containing structure. Possible parameters are values for struct fields separated with colon and
        optional struct length defined with `length=`. Length can be used in receiveing to validate that struct matches
        predfeined length. When sending, the struct length can refer to other message field which will then be set
        dynamically.
        """
        configs, parameters, _ = self._get_parameters_with_defaults(parameters)
        self._message_stack.append(StructTemplate(type, name, self._current_container, parameters, length=configs.get('length')))

    def end_struct(self):
        """End struct definition. See `Struct`."""
        struct = self._message_stack.pop()
        self._add_field(struct)

    def new_list(self, size, name):
        """Defines a new list to template of `size` and with `name`.

        List type must be given after this keyword by defining one field. Then the list definition has to be closed using
        `End List`.
        """
        self._message_stack.append(ListTemplate(size, name, self._current_container))

    def end_list(self):
        """End list definition. See `New List`.
        """
        list = self._message_stack.pop()
        self._add_field(list)

    def new_binary_container(self, name):
        """Defines a new binary container to template.

        Binary container can only contain binary fields defined with `Bin` keyword.
        """
        self._message_stack.append(BinaryContainerTemplate(name, self._current_container))

    def new_tbcd_container(self, name):
        self._message_stack.append(TBCDContainerTemplate(name, self._current_container))

    def end_binary_container(self):
        """End binary container. See `New Binary Container`.
        """
        binary_container = self._message_stack.pop()
        binary_container.verify()
        self._add_field(binary_container)

    def end_tbcd_container(self):
        tbcd_container = self._message_stack.pop()
        self._add_field(tbcd_container)

    def bin(self, size, name, value=None):
        """Add new binary field to template.

        This keyword has to be called within a binary container. See `New Binary Container`.
        """
        self._add_field(Binary(size, name, value))

    def tbcd(self, name, value):
        self._add_field(TBCD(name, value))

    def union(self, type, name):
        """Defines a new union to template of `type` and `name`.

        Fields inside the union are alternatives and the length of the union is the length of its longest field.
        """
        self._message_stack.append(UnionTemplate(type, name, self._current_container))

    def end_union(self):
        """End union definition. See `Union`.
        """
        union = self._message_stack.pop()
        self._add_field(union)

    def pdu(self, length):
        """Defines the message in protocol template.

        Length must be the name of a previous field in template definition."""
        self._add_field(PDU(length))

    def hex_to_bin(self, hex_value):
        """Converts given hex value to binary.
        """
        return to_bin(hex_value)

    def bin_to_hex(self, bin_value):
        """Converts given binary to hex string.
        """
        return to_0xhex(bin_value)

    def _get_parameters_with_defaults(self, parameters):
        config, fields, headers = self._parse_parameters(parameters)
        fields = self._populate_defaults(fields)
        return config, fields, headers

    def _populate_defaults(self, fields):
        ret_val = self._field_values
        ret_val.update(fields)
        self._field_values = {}
        return ret_val 

    def value(self, name, value):
        """Defines a default `value` for a template field identified by `name`.
        """
        self._field_values[name] = value

    def _parse_parameters(self, parameters):
        configs, fields = [], []
        for parameter in parameters:
            self._parse_entry(parameter, configs, fields)
        headers, fields = self._get_headers(fields)
        return self._to_dict(configs, fields, headers)

    def _get_headers(self, fields):
        headers = []
        header_indexes = []
        for index, (name, value) in enumerate(fields):
            if name == 'header' and ':' in value:
                headers.append(value.split(':', 1))
                header_indexes.append(index)
        fields = (field for index, field in enumerate(fields)
                  if index not in header_indexes)
        return headers, fields
    
    def _to_dict(self, *lists):
        return (dict(list) for list in lists)

    def _parse_entry(self, param, configs, fields):
        colon_index = param.find(':')
        equals_index = param.find('=')
        # TODO: Cleanup. There must be a cleaner way.
        # Luckily test_rammbock.py has unit tests covering all paths.
        if colon_index == equals_index == -1:
            raise Exception('Illegal parameter %s' % param)
        elif equals_index == -1:
            fields.append(self._name_and_value(':', param))
        elif colon_index == -1 or colon_index > equals_index:
            configs.append(self._name_and_value('=', param))
        else:
            fields.append(self._name_and_value(':', param))

    def _name_and_value(self, separator, parameter):
        index = parameter.find(separator)
        try:
            key = str(parameter[:index].strip())
        except UnicodeError:
            raise Exception("Only ascii characters are supported in parameters.")
        return (key, parameter[index + 1:].strip())

    def _log_msg(self, loglevel, log_msg):
        print '*%s* %s' % (loglevel, log_msg)

