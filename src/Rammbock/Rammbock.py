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
from __future__ import with_statement

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
POSSIBLE_LOG_LEVELS = ["WARN", "INFO", "DEBUG", "TRACE"]

class Rammbock(object):

    def __init__(self):
        self._data = ""
        self._servers = {}
        self._clients = {}
        self._binary = ""
        self._last_created_server = None
        self._last_created_client = None

    def create_udp_server(self, ip, port, name=Server.DEFAULT_NAME):
        """Creates Server which expects UDP as a transport layer protocol

        'ip' and 'port' are telling which ip-address and port server is going to be bind. Optionally server name can be stated, usually used when multiple servers are needed

        Examples:
        | Create UDP Server | 10.10.10.2 | 53 | DNS_Server1 |
        """
        self.server_should_not_be_running(name, "UDP")
        self._servers[name] = UDPServer(name)
        self._servers[name].server_startup(ip, port)
        self._last_created_server = name

    def create_sctp_server(self, ip, port, name=Server.DEFAULT_NAME):
        """Creates Server which expects SCTP as a transport layer protocol

        'ip' and 'port' are telling which ip-address and port server is going to be bind. Optionally server name can be stated, usually used when multiple servers are needed

        Examples:
        | Create SCTP Server | 10.10.10.2 | 3868 | Diameter_Server1 |
        """
        self.server_should_not_be_running(name, "SCTP")
        self._servers[name] = SCTPServer(name)
        self._servers[name].server_startup(ip, port)
        self._last_created_server = name

    def create_tcp_server(self, ip, port, name=Server.DEFAULT_NAME):
        """Creates Server which expects TCP as a transport layer protocol

        'ip' and 'port' are telling which ip-address and port server is going to be bind. Optionally server name can be stated, usually used when multiple servers are needed

        Examples:
        | Create SCTP Server | 10.10.10.2 | 80 | HTTP_Server1 |
        """
        self.server_should_not_be_running(name, "TCP")
        self._servers[name] = TCPServer(name)
        self._servers[name].server_startup(ip, port)
        self._last_created_server = name

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
            return self._last_created_client
        return name

    def _use_latest_server_name_if_name_not_present(self, name):
        if not name:
            return self._last_created_server
        return name

    def server_accepts_tcp_connection(self, server_name=None, connection_alias=None):
        """ Accepts TCP connection from client. Server name can be given optionally

        Examples:
        | Server Accepts TCP Connection | | # last created server is used |
        | Server Accepts TCP connection | HTTP_Server1 | # Given TCP Server is used |
        """
        server_name = self._use_latest_server_name_if_name_not_present(server_name)
        self._servers[server_name].accept_connection(connection_alias)

    def server_accepts_sctp_connection(self, server_name=None, connection_alias=None):
        """ Accepts TCP connection from client. Server name can be given optionally

        Examples:
        | Server Accepts TCP Connection | | # last created server is used |
        | Server Accepts TCP Connection | HTTP_Server1 | # Given TCP Server is used |
        """
        server_name = self._use_latest_server_name_if_name_not_present(server_name)
        self._servers[server_name].accept_connection(connection_alias)

    def delete_server(self, name=None):
        """ Deletes given server. If no server name stated, deletes last created.

        Examples:
        | Delete Server | DNS_Server1 | #Deletes given server |
        | Delete Server | | #Deletes last created server |
        """
        name = self._use_latest_server_name_if_name_not_present(name)
        self._servers[name].close()
        del self._servers[name]

    def create_udp_client(self, name=Client.DEFAULT_NAME, ip=None):
        """ Creates UDP Client. Name and IP-address of the client can be given

        Examples:
        | Create UDP Client | DNS_Client1 | 10.10.10.2 | # Name and IP are given |
        | Create UDP Client | DNS_Client1 |  | # Name is given |
        | Create UDP Client | | | |
        """
        self.client_should_not_be_running(name, "UDP")
        self._clients[name] = UDPClient(name, ip)
        self._last_created_client = name

    def create_sctp_client(self, name=Client.DEFAULT_NAME, ip=None):
        """ Creates SCTP Client. Name and IP-address of the client can be given

        Examples:
        | Create SCTP Client | Diameter_Client1 | 10.10.10.2 | # Name and IP are given |
        | Create SCTP Client | Diameter_Client1 |  | # Name is given |
        | Create SCTP Client | | | |
        """
        self.client_should_not_be_running(name, "SCTP")
        self._clients[name] = SCTPClient(name, ip)
        self._last_created_client = name

    def create_tcp_client(self, name=Client.DEFAULT_NAME, ip=None):
        """ Creates TCP Client. Name and IP-address of the client can be given

        Examples:
        | Create TCP Client | DNS_Client1 | 10.10.10.2 | # Name and IP are given |
        | Create TCP Client | DNS_Client1 |  | # Name is given |
        | Create TCP Client | | | |
        """
        self.client_should_not_be_running(name, "TCP")
        self._clients[name] = TCPClient(name, ip)
        self._last_created_client = name

    def delete_client(self, name=None):
        """ Deletes given client. If no client name stated, deletes last created.

        Examples:
        | Delete Client | DNS_Client1 | #Deletes given client |
        | Delete Client | | #Deletes last created client |
        """
        name = self._use_latest_client_name_if_name_not_present(name)
        self._clients[name].close()
        del self._clients[name]

    def client_sends_data(self, data=None, client_name=None):
        """Client Send Data which have been created to the message or string can be set as 'data'. Used client can be stated.

        Examples:
        | Client Sends Data | | |
        | Client Sends Data | FooBar | |
        | Client Sends Data | FooBar | HTTP_Client1 |
        """
        client_name = self._use_latest_client_name_if_name_not_present(client_name)
        self.client_should_be_running(client_name)
        if data:
            self._clients[client_name].send_packet(data)
        else:
            self._clients[client_name].send_packet(self._data)

    def server_receives_data(self, name=None, connection_alias=None):
        """ Server receives data from client. Name and connection alias can be stated.

        Examples:
        |Server Receives Data | | |
        |Server Receives Data| HTTP_Server1 | Connection1 |
        """
        name = self._use_latest_server_name_if_name_not_present(name)
        return self.server_receives_data_and_address(name, connection_alias)[0]

    def server_receives_data_and_address(self, name=None, connection_alias=None):
        """ Server return data, Client IP-address and port. Server name and connection alias can be also set

        Examples:
        | ${data} | ${ip} | ${port} = | Server Receives Data and Address  | HTTP_Server1 | Connection1 | #Receives data from certain Server and connection |
        | ${data} | ${ip} | ${port} = | Server Receives Data and Address  | | | #Receives data from last created Server |
        """
        name = self._use_latest_server_name_if_name_not_present(name)
        self._data, ip, port = self._servers[name].server_receives_data_and_address(connection_alias)
        print "Data received from %s:%s :%s" % (ip, port, self._data)
        return self._data, ip, port

    def client_receives_data(self, name=Client.DEFAULT_NAME):
        """Return anything that is currently in the socket at the moment. Client name can be given.

        Examples:
        | Client Receives Data | |
        | Client Receives Data | HTTP_Client |
        """
        self._data = self._clients[name].receive_data()
        print "Data received:", self._data
        return self._data

    def server_sends_data(self, data=None, name=None):
        """Server Send Data which have been created to the message or string can be set as 'data'. Used server can be stated.

        Examples:
        | Server Sends Data | | |
        | Server Sends Data | FooBar | |
        | Server Sends Data | FooBar | HTTP_Client1 |
        """
        name = self._use_latest_server_name_if_name_not_present(name)
        if data:
            data_to_send = data
        else:
            data_to_send = self._data
        self._servers[name].send_data(data_to_send)
        print "Data sent:", data_to_send

    def reset_message(self):
        """ Empties message.
        """
        self._data = ""
        self._binary = ""

    def add_string(self, value, length=None, encoding=None):
        """
        Add string to the message. 'value' is string, 'length' adds possible padding to end of the string. 'encoding' sets encoding, utf-8 is default.

        Examples:
        | Add String | Host: www.nokiasiemensnetworks.com | | | # add string |
        | Add String | Host: www.nokiasiemensnetworks.com | encoding=unicode | | # add string in unicode |
        | Add String | Host: www.nokiasiemensnetworks.com | 25 | unicode | # add string of length 25 in unicode |
        """
        if encoding:
            value = value.encode(encoding)
        if not length:
            length = len(value)
        self._data += str(value).rjust(int(length), '\0')

    def add_integer_as_octets(self, value, length, base=10):
        """
        Adds decimal number as octets. Length as octest can be give. base can be stated as an argument.

        Examples:
        | Add Decimal as Octets | 42 | 1 | |#Adds number 42 as one octet to message. |
        | Add Decimal as Octets | 42 | 2 | |#Adds number 42 as two octets to message. Padding is added |
        | Add Decimal as Octets | 2A | 1 | 16 |#Adds number 42 presented as hexadecimal in one octet to message. |
        | Add Decimal as Octets | 0B00101010 | 1 | 2 | #Adds number 42 presented as bit in one octet to message. |
        | Add Decimal as Octets | 0O52 | 1 | 8|  #Adds number 42 presented as octal in one octet to message. |
        """
        value = str(int(str(value), int(base)))
        if not int(length):
            return
        data = self._convert_to_hex_and_add_padding(value, length)
        if len(data) > int(length) * 2:
            raise Exception("Value is too big for length")
        while data:
            self._data += pack('B', int(data[:2], 16))
            data = data[2:]

    def add_integer_as_bits(self, value, length):
        """
        Adds integer as bits. Length how many bits is used, can be given.

        Examples:
        |Add Integer as Bits | 42 | 6 |
        """
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
        """
        Set string to the message, which can be send.

        Example:
        | Set Message | FooBar |
        """
        self._data = message

    def get_message(self):
        """
        Returns the current message as hex stream.

        Examples:
        | Get Message |
        """
        return self._data

    def log_message(self, level="INFO"):
        """
        Logs the current message. Uses given level parameter as log level or INFO as DEFAULT_NAME

        Possible log levels are:
        WARN, INFO, DEBUG, TRACE

        Examples
        | Log Message |
        | Log Message | DEBUG | # uses DEBUG log level
        """
        if level not in POSSIBLE_LOG_LEVELS:
            raise Exception("Unknown log level! Possible levels are %s" % (POSSIBLE_LOG_LEVELS,))
        print '*' + level + '*', self._data

    def log_message_to_file(self, file):
        """
        Logs current message into a file. If file given as parameter is present, 
        this keyword will overwrite it. File will be created to working directory
        if full path is not given.

        Examples:
        | Log Message To File | foo | # logs current message to file called foo to working directory|
        | Log Message To File | /tmp/foo | # logs current message to file called foo in /tmp/ directory |
        | Log Message To File | C:\temp\foo | # logs current message to file called foo in  C:\temp\ directory |

        """
        with open(file,'w') as writeable:
            writeable.write(self._data)

    def _read_until(self, delimiter=None, encoding='utf-8'):
        if delimiter:
            i,self._data = self._data.split(str(delimiter),1)
            return i.decode(encoding)
        return self._data.decode(encoding)

    def read_integer_from_octets(self, length):
        """
        Reads integer from message. 'lenght' how many octets are read can be stated.

        Examples:
        | ${ie_1} | Read Integer From Octets | 2 |
        """
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
        """"
        Add telephone binary coded decimal (TBCD).

        Example:
        | Add TBCD | 358600064644 |
        """
        nmbr = "".join(numbers)
        while len(nmbr) > 1:
            self.add_integer_as_bits(int(nmbr[1]), 4)
            self.add_integer_as_bits(int(nmbr[0]), 4)
            nmbr = nmbr[2:]
        if nmbr:
            self.add_integer_as_bits(15, 4)
            self.add_integer_as_bits(int(nmbr[0]), 4)

    def add_ip(self, address):
        """
        Add ip 'address' as hex. Every ip-number field is expressed as two number hexadecimal.

        Example:
        | Add Ip | 10.0.0.1 |
        """
        if not IP_REGEX.match(address):
            raise Exception("Not a valid ip Address")
        for a in address.split('.'):
            self.add_integer_as_octets(a, 1)

    # TODO: only have these methods: read_octets(len, base) and read_binary(len) and read_string(len, encoding)
    def read_hex_data(self, length, no_prefix=None):
        a = ""
        if not no_prefix:
            a += "0x"
        return a + "".join(hex(int(self.read_integer_from_octets(1)))[2:].rjust(2, '0') for _ in range(int(length)))

    def read_tbcd(self, amount):
        """
        Reads TBCD number from message and returns it as integer. 'amount' of numbers which are read from data can be stated.

        Examples:
        | Read TBCD | 7 |
        """
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
    def read_ip(self):
        """
        Read Ip from hexadecimal presentation.

        Examples:
        | ${ip_address}= | Read IP |
        """
        return  ".".join(str(self.read_integer_from_octets(1)) for _ in range(4))

    def read_string(self, length=None, delimiter=None, encoding=None):
        """
        Reads string of text from message. 
        If delimiter is given, tries to read untitil given delimiter is found. 
        If length is given reads the amount of bytes and converts it to string.
        If encoding parameter is given converts the string to given encoding.
        Note that if we read utf-8 characters like &ouml; or &auml; the character length
        is more than 1 byte

        Examples:
        | Read String | length=10 |
        | Read String | delimiter=\\n |
        | Read String | length=10 | encoding=utf-8 |
        """
        read = ""
        if delimiter:
            read = self._read_until(delimiter)
        elif length:
            if length == "*":
                read = self._data
                self._data = ""
            else:
                read = self._data[:int(length)]
                self._data = self._data[int(length):]
        if encoding:
            return read.decode(encoding)
        return read

    def sctp_should_be_supported(self):
        """
        Checks if SCTP support is available in this platform. Fails if SCTP support is not available

        Examples:
        | SCTP should be supported | # keyword will pass if SCTP support is enabled |
        | SCTP should be supported | # keyword will fail if SCTP support is not enabled |

        """
        if not Server.SCTP_ENABLED:
            raise AssertionError("SCTP not available on this platform.")
