#  Copyright 2011 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

#!/usr/bin/python
#-*- coding: iso-8859-15 -*-
#
from Client import UDPClient, TCPClient, SCTPClient
from Server import UDPServer, TCPServer, SCTPServer
import Server
import Client
from struct import pack, unpack
import re

IP_REGEX = re.compile(r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b")

d2b = lambda d: (not isinstance(d, int) or (not d)) and '0' \
    or (d2b(d//2)+str(d%2))

SERVER_ALREADY_CREATED = "There is already one %s Server created. You need to specify a unique name for a new server"
CLIENT_ALREADY_CREATED = "There is already one %s Client created. You need to specify a unique name for a new clients"

class Rammbock(object):

    def __init__(self):
        self._data = ""
        self._servers = {}
        self._clients = {}
        self._binary = ""
        self._tbcd = ""
        last_created_server = None
        last_created_client = None

    def create_udp_server(self, ip, port, name=Server.DEFAULT_NAME):
        """Creates Server which expects UDP as a transport layer protocol

        'ip' and 'port' are telling which ip-address and port server is going to be bind. Optionally server name can be stated, usually used when multiple servers are needed

        Examples:
        | Create UDP Server | 10.10.10.2 | 53 | DNS_Server1 |
        """
        self.server_should_not_be_running(name, "UDP")
        self._servers[name] = UDPServer(name)
        self._servers[name].server_startup(ip, port)
        self.last_created_server = name

    def create_sctp_server(self, ip, port, name=Server.DEFAULT_NAME):
        """Creates Server which expects SCTP as a transport layer protocol

        'ip' and 'port' are telling which ip-address and port server is going to be bind. Optionally server name can be stated, usually used when multiple servers are needed

        Examples:
        | Create SCTP Server | 10.10.10.2 | 3868 | Diameter_Server1 |
        """
        self.server_should_not_be_running(name, "SCTP")
        self._servers[name] = SCTPServer(name)
        self._servers[name].server_startup(ip, port)
        self.last_created_server = name

    def create_tcp_server(self, ip, port, name=Server.DEFAULT_NAME):
        """Creates Server which expects TCP as a transport layer protocol

        'ip' and 'port' are telling which ip-address and port server is going to be bind. Optionally server name can be stated, usually used when multiple servers are needed

        Examples:
        | Create SCTP Server | 10.10.10.2 | 80 | HTTP_Server1 |
        """
        self.server_should_not_be_running(name, "TCP")
        self._servers[name] = TCPServer(name)
        self._servers[name].server_startup(ip, port)
        self.last_created_server = name

    def server_should_not_be_running(self, name, protocol=""):
        """Raises exception if given server exist

        Example:
        | Server Should Not be Running | DNS_Server1 |
        """
        if name in self._servers:
            raise Exception(SERVER_ALREADY_CREATED % (protocol,))

    def server_should_be_running(self, name=None):
        """Raises exception if given server does not exist

        Example:
        | Server Should be Running | DNS_Server1 |
        """
        name = self._use_latest_server_name_if_name_not_present(name)
        if not name in self._servers:
            raise Exception("Server %s not set up" % (name,))

    def client_should_be_running(self, name=None):
        """Raises exception if given client does not exist

        Example:
        | Server Should be Running | DNS_Client1 |
        """
        name = self._use_latest_client_name_if_name_not_present(name)
        if not name in self._clients:
            raise Exception("Client %s not set up" % (name,))

    def client_should_not_be_running(self, name, protocol=""):
        """Raises exception if given server exist

        Example:
        | Server Should Not be Running | DNS_Server1 |
        """
        if name in self._clients:
            raise Exception(CLIENT_ALREADY_CREATED % (protocol,))

    def client_connects_to_udp_server(self, host, port, client_name=None):
        """ Given UDP client connects to server. Server IP-address and port need to be given. If no client stated, last created client is used.

        Examples:
        | Client Connects to UDP Server | 10.10.10.2 | DNS_Client1 | #Client name is stated |
        | Client Connects to UDP Server | 10.10.10.2 | | # Last created client is used |
        """
        client_name = self._use_latest_client_name_if_name_not_present(client_name)
        self._clients[client_name].establish_connection_to_server(host, port)

    def client_connects_to_tcp_server(self, host, port, client_name=None):
        """ Given TCP client connects to server. Server IP-address and port need to be given. If no client stated, last created client is used.

        Examples:
        | Client Connects to TCP Server | 10.10.10.2 | HTTP_Client1 | #Client name is stated |
        | Client Connects to TCP Server | 10.10.10.2 | | # Last created client is used |
        """
        client_name = self._use_latest_client_name_if_name_not_present(client_name)
        self._clients[client_name].establish_connection_to_server(host, port)

    def client_connects_to_sctp_server(self, host, port, client_name=None):
        """ Given SCTP client connects to server. Server IP-address and port need to be given. If no client stated, last created client is used.

        Examples:
        | Client Connects to SCTP Server | 10.10.10.2 | Diameter_Client1 | #Client name is stated |
        | Client Connects to SCTP Server | 10.10.10.2 | | # Last created client is used |
        """
        client_name = self._use_latest_client_name_if_name_not_present(client_name)
        self._clients[client_name].establish_connection_to_server(host, port)

    def _use_latest_client_name_if_name_not_present(self, name):
        if not name:
            return self.last_created_client
        return name

    def _use_latest_server_name_if_name_not_present(self, name):
        if not name:
            return self.last_created_server
        return name

    def server_accepts_tcp_connection(self, server_name=None, connection_alias=None):
        server_name = self._use_latest_server_name_if_name_not_present(server_name)
        self._servers[server_name].accept_connection(connection_alias)

    def server_accepts_sctp_connection(self, server_name=None, connection_alias=None):
        server_name = self._use_latest_server_name_if_name_not_present(server_name)
        self._servers[server_name].accept_connection(connection_alias)

    def delete_server(self, name=None):
        name = self._use_latest_server_name_if_name_not_present(name)
        self._servers[name].close()
        del self._servers[name]

    def create_udp_client(self, name=Client.DEFAULT_NAME, ip=None):
        self.client_should_not_be_running(name, "UDP")
        self._clients[name] = UDPClient(name, ip)
        self.last_created_client = name

    def create_sctp_client(self, name=Client.DEFAULT_NAME, ip=None):
        self.client_should_not_be_running(name, "SCTP")
        self._clients[name] = SCTPClient(name, ip)
        self.last_created_client = name

    def create_tcp_client(self, name=Client.DEFAULT_NAME, ip=None):
        self.client_should_not_be_running(name, "TCP")
        self._clients[name] = TCPClient(name, ip)
        self.last_created_client = name

    def delete_client(self, name=None):
        name = self._use_latest_client_name_if_name_not_present(name)
        self._clients[name].close()
        del self._clients[name]

    def client_sends_data(self, data=None, client_name=None):
        client_name = self._use_latest_client_name_if_name_not_present(client_name)
        self.client_should_be_running(client_name)
        if data:
            self._clients[client_name].send_packet(data)
        else:
            self._clients[client_name].send_packet(self._data)
            print "Data sent:", self._data

    def server_receives_data(self, name=None, connection_alias=None):
        name = self._use_latest_server_name_if_name_not_present(name)
        return self.server_receives_data_and_address(name, connection_alias)[0]

    def server_receives_data_and_address(self, name=None, connection_alias=None):
        name = self._use_latest_server_name_if_name_not_present(name)
        self._data, ip, port = self._servers[name].server_receives_data_and_address(connection_alias)
        print "Data received from %s:%s :%s" % (ip, port, self._data)
        return self._data, ip, port

    def client_receives_data(self, name=Client.DEFAULT_NAME):
        """This method will return anything that is currently in the socket at the moment. 
        There is no packet length checking currently implemented. """
        self._data = self._clients[name].receive_data()
        print "Data received:", self._data
        return self._data

    def server_sends_data(self, data=None, name=None):
        name = self._use_latest_server_name_if_name_not_present(name)
        if data:
            data_to_send = data
        else:
            data_to_send = self._data
        self._servers[name].send_data(data_to_send)
        print "Data sent:", data_to_send

    def reset_message(self):
        self._data = ""
        self._binary = ""

    # TODO: add encoding argument
    def add_string(self, value, length=None):
        if not length:
            length = len(value)
        self._data += str(value).rjust(int(length), '\0')

    # TODO: add octets and add bits. both support several bases.
    def add_decimal_as_octets(self, value, length):
        if not int(length):
            return
        data = self._convert_to_hex_and_add_padding(value, length)
        if len(data) > int(length) * 2:
            raise Exception("Value is too big for length")
        while data:
            self._data += pack('B', int(data[:2], 16))
            data = data[2:]

    # TODO: add as bits. b1010111 kuinka base annetaan robotissa?
    def add_decimal_as_bits(self, value, length):
        data = d2b(int(value))[1:].rjust(int(length), '0')
        if len(data) > int(length):
            raise Exception("Value is too big for length")
        self._binary += data
        while len(self._binary) >= 8:
            self._data += pack('B', int(self._binary[:8], 2))
            self._binary = self._binary[8:]

    def _convert_to_hex_and_add_padding(self, value, length):
        data = hex(int(value))[2:]
        if data.endswith('L'):
            data = data[:-1]
        return data.rjust(int(length)*2, '0')

    def set_message(self, message):
        self._data = message

    def get_message(self):
        return self._data

    def log_message(self, level="INFO"):
        print '*' + level + '*', self._data

    def log_message_to_file(self, file):
        with open(file,'w') as writeable:
            input.write(self._data)

    def _read_until(self, delimiter=None):
        if delimiter:
            i,self._data = self._data.split(str(delimiter),1)
            return i
        return self._data

    def read_from_data(self, length):
        if not int(length):
            return
        return str(int("".join(self._read_from_data(int(length))), 16))

    def _read_from_data(self, length):
        for d in self._data[:length]:
            yield hex((unpack('B', d)[0]))[2:].rjust(2, '0')
        self._data = self._data[int(length):]

    def read_binary(self, length):
        if len(self._binary) < int(length):
            real_length = (((int(length) - len(self._binary)) - 1) / 8) + 1
            self._read_binary_from_data(real_length)
        return self._read_from_binary(length)

    def _read_binary_from_data(self, length):
        self._binary += "".join(self._get_binary_from_data(int(length)))

    def _get_binary_from_data(self, length):
        for d in self._data[:length]:
            yield d2b(int(str(unpack('B', d)[0])))[1:].rjust(8, '0')
        self._data = self._data[int(length):]

    def _read_from_binary(self, length):
        length = int(length)
        if len(self._binary) < length:
            raise Exception("Not enough bits to read")
        value = self._binary[:length]
        self._binary = self._binary[length:]
        return str(int(value,2))

    def add_tbcd(self, *numbers):
        nmbr = "".join(numbers)
        while len(nmbr) > 1:
            self.add_decimal_as_bits(int(nmbr[1]), 4)
            self.add_decimal_as_bits(int(nmbr[0]), 4)
            nmbr = nmbr[2:]
        if nmbr:
            self.add_decimal_as_bits(15, 4)
            self.add_decimal_as_bits(int(nmbr[0]), 4)

    def add_ip(self, address):
        if not IP_REGEX.match(address):
            raise Exception("Not a valid ip Address")
        for a in address.split('.'):
            self.add_decimal_as_octets(int(a), 1)

    def add_hex_data(self, data, length):
        if int(length) < len(data[2:])/2:
            raise Exception("Value is too big for length")
        try:
            self.add_decimal_as_octets(str(int(data,16)),length)
        except ValueError:
            raise Exception("Value is not valid hex")

    # TODO: only have these methods: read_octets(len, base) and read_binary(len) and read_string(len, encoding)
    def read_hex_data(self, length, no_prefix=None):
        a = ""
        if not no_prefix:
            a += "0x"
        return a + "".join(hex(int(self.read_from_data(1)))[2:].rjust(2, '0') for _ in range(int(length)))

    def read_tbcd(self, amount):
        tbcd = ""
        length = (int(amount)/2)+(int(amount)%2)
        self._read_binary_from_data(length)
        while len(self._binary) > 8:
            a = self._read_from_binary(4)
            b = self._read_from_binary(4)
            tbcd += str(b) + str(a)
        a = self._read_from_binary(4)
        b = self._read_from_binary(4)
        tbcd += str(b)
        if int(a) < 10:
            tbcd += str(a)
        return tbcd

    # TODO: read hex
    def read_ip_from_hex(self):
        return  ".".join(str(self.read_from_data(1)) for _ in range(4))

    def read_string(self, length=None, delimiter=None):
        if delimiter:
            return self._read_until(delimiter)
        string = self._data[:int(length)]
        self._data = self._data[int(length):]
        return string

    def sctp_should_be_supported(self):
        if not Server.SCTP_ENABLED:
            raise AssertionError("SCTP not available on this platform.")
