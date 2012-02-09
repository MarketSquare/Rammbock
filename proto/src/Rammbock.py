# API prototype
import time
from Network import TCPServer
from Network import TCPClient
from Network import UDPServer, UDPClient, _NamedCache

from Protocol import Protocol, UInt, PDU
from binary_conversions import to_0xhex, to_bin, to_bin_of_length, to_hex

class Rammbock(object):

    def __init__(self):
            self._init_caches()

    def _init_caches(self):
        self._protocol_in_progress = None
        self._protocols = {}
        self._servers = _NamedCache('server')
        self._clients = _NamedCache('client')

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
        self._protocol_in_progress = Protocol(protocol_name)

    def end_protocol_description(self):
        """End protocol definition."""
        self._protocols[self._protocol_in_progress.name] = self._protocol_in_progress
        self._protocol_in_progress = None

    def start_udp_server(self, _ip, _port, _name=None, _timeout=None, _protocol=None):
        protocol = self._protocols[_protocol] if _protocol else None
        server = UDPServer(ip=_ip, port=_port, timeout=_timeout, protocol=protocol)
        return self._servers.add(server, _name)

    def start_udp_client(self, _ip=None, _port=None, _name=None, _timeout=None, _protocol=None):
        protocol = self._protocols[_protocol] if _protocol else None
        client = UDPClient(timeout=_timeout, protocol=protocol)
        if _ip or _port:
            client.set_own_ip_and_port(ip=_ip, port=_port)
        return self._clients.add(client, _name)

    def start_tcp_server(self, _ip, _port, _name=None, _timeout=None, _protocol=None):
        protocol = self._protocols[_protocol] if _protocol else None
        server = TCPServer(ip=_ip, port=_port, timeout=_timeout, protocol=protocol)
        return self._servers.add(server, _name)

    def start_tcp_client(self, _ip=None, _port=None, _name=None, _timeout=None, _protocol=None):
        protocol = self._protocols[_protocol] if _protocol else None
        client = TCPClient(timeout=_timeout, protocol=protocol)
        if _ip or _port:
            client.set_own_ip_and_port(ip=_ip, port=_port)
        return self._clients.add(client, _name)

    def accept_connection(self, _name=None, _alias=None):
        server = self._servers.get(_name)
        server.accept_connection(_alias)

    def connect(self, host, port, _name=None):
        """Connect a client to certain host and port."""
        client = self._clients.get(_name)
        client.connect_to(host, port)

    # TODO: Log the raw binary that is sent and received.
    def client_sends_binary(self, message, _name=None):
        """Send raw binary data."""
        client = self._clients.get(_name)
        client.send(message)

    def server_sends_binary(self, message, _name=None, _connection=None):
        """Send raw binary data."""
        server = self._servers.get(_name)
        server.send(message, alias=_connection)

    def client_receives_binary(self, _name=None, _timeout=None):
        """Receive raw binary data."""
        client = self._clients.get(_name)
        return client.receive(timeout=_timeout)

    def server_receives_binary(self, _name=None, _timeout=None, _connection=None):
        """Receive raw binary data."""
        return self.server_receives_binary_from(_name, _timeout, _connection)[0]

    def server_receives_binary_from(self, _name=None, _timeout=None, _connection=None):
        """Receive raw binary data. Returns message, ip, port"""
        server = self._servers.get(_name)
        return server.receive_from(timeout=_timeout, alias=_connection)

    def new_message(self, protocol=None, *parameters):
        """Define a new message template.
    
        Parameters have to be header fields."""
        raise Exception('NYI')

    def get_message(self, *params):
        """Get encoded message.

        * Send Message -keywords are convenience methods, that will call this to get the message object and then send it.
        Parameters have to be pdu fields."""
        raise Exception('NYI')

    def client_sends_message(self, *params):
        """Send a message.
    
        Parameters have to be message fields."""
        raise Exception('NYI')

    def server_sends_message(self, *params):
        """Send a message.
    
        Parameters have to be message fields."""
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
        self._add_field(UInt(length, name, value))

    def _add_field(self, field):
        if self._protocol_in_progress:
            self._protocol_in_progress.add(field)
        else:
            raise Exception('NYI')

    def pdu(self, length):
        """Defines the message in protocol template.

        Length must be the name of a previous field in template definition."""
        self._add_field(PDU(length))

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

