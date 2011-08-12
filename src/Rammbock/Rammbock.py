#!/usr/bin/python
#-*- coding: iso-8859-15 -*-
#
from Client import UDPClient, TCPClient, SCTPClient
from Server import UDPServer, TCPServer, SCTPServer
import Server
import Client
import struct
import re

IP_REGEX = re.compile(r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b")

d2b = lambda d: (not isinstance(d, int) or (not d)) and '0' \
    or (d2b(d//2)+str(d%2))


class Rammbock(object):

    IE_NOT_FOUND = "Information Element does not exist: '%s'"
    HEADER_NOT_FOUND = "Header does not exist: '%s'"
    BINARY_NOT_FOUND = "Header does not exist: '%s'"

    def __init__(self):
        self._data = ""
        self._servers = {}
        self._clients = {}
        self._binary = ""
        self._tbcd = ""

    def start_udp_server(self, ip, port, name=Server.DEFAULT_NAME):
        self._servers[name] = UDPServer(name)
        self._servers[name].server_startup(ip, port)

    def start_sctp_server(self, ip, port, name=Server.DEFAULT_NAME):
        self._servers[name] = SCTPServer(name)
        self._servers[name].server_startup(ip, port)

    def start_tcp_server(self, ip, port, name=Server.DEFAULT_NAME):
        self._servers[name] = TCPServer(name)
        self._servers[name].server_startup(ip, port)

    def check_server_status(self, name=Server.DEFAULT_NAME):
        return name in self._servers

    def check_client_status(self, name=Client.DEFAULT_NAME):
        return name in self._clients

    def connect_to_udp_server(self, host, port, client=Client.DEFAULT_NAME):
        self._clients[client].establish_connection_to_server(host, port)

    def connect_to_tcp_server(self, host, port, client=Client.DEFAULT_NAME):
        self._clients[client].establish_connection_to_server(host, port)

    def connect_to_sctp_server(self, host, port, client=Client.DEFAULT_NAME):
        self._clients[client].establish_connection_to_server(host, port)

    def accept_tcp_connection(self, server=Server.DEFAULT_NAME, connection_alias=None):
        self._servers[server].accept_connection(connection_alias)

    def accept_sctp_connection(self, server=Server.DEFAULT_NAME, connection_alias=None):
        self._servers[server].accept_connection(connection_alias)

    def close_server(self, name=Server.DEFAULT_NAME):
        self._servers[name].close()
        del self._servers[name]

    def create_udp_client(self, name=Client.DEFAULT_NAME, ip=None):
        self._clients[name] = UDPClient(name, ip)

    def create_sctp_client(self, name=Client.DEFAULT_NAME, ip=None):
        self._clients[name] = SCTPClient(name, ip)

    def create_tcp_client(self, name=Client.DEFAULT_NAME, ip=None):
        self._clients[name] = TCPClient(name, ip)

    def close_client(self, name=Client.DEFAULT_NAME):
        self._clients[name].close()
        del self._clients[name]

    def client_sends_data(self, packet=None, name=Client.DEFAULT_NAME):
        if packet:
            self._clients[name].send_packet(packet)
        else:
            self._clients[name].send_packet(self._data)
            print "Data sent:", self._data

    def server_receives_data(self, name=Server.DEFAULT_NAME, connection_alias=None):
        return self.server_receives_data_and_address(name, connection_alias)[0]

    def server_receives_data_and_address(self, name=Server.DEFAULT_NAME, connection_alias=None):
        self._data, ip, port = self._servers[name].server_receives_data_and_address(connection_alias)
        print "Data received from %s:%s :%s" % (ip, port, self._data)
        return self._data, ip, port

    def client_receives_data(self, name=Client.DEFAULT_NAME):
        self._data = self._clients[name].receive_data()
        print "Data received:", self._data
        return self._data

    def server_sends_data(self, packet=None, name=Server.DEFAULT_NAME):
        if packet:
            self._servers[name].send_data(packet)
        else:
            self._servers[name].send_data(self._data)
            print "Data sent:", self._data

    def create_message(self):
        self._data = ""
        self._binary = ""


    def add_string(self, value, length=None):
        if not length:
            length = len(value)
        self._data += str(value).rjust(int(length), '\0')

    def add_decimal_as_octets(self, value, length):
        if not int(length):
            return
        data = self._convert_to_hex_and_add_padding(value, length)
        if len(data) > int(length) * 2:
            raise Exception("Value is too big for length")
        while data:
            self._data += struct.pack('B', int(data[:2], 16))
            data = data[2:]

    def add_decimal_as_bits(self, value, length):
        data = d2b(int(value))[1:].rjust(int(length), '0')
        if len(data) > int(length):
            raise Exception("Value is too big for length")
        self._binary += data
        while len(self._binary) >= 8:
            self._data += struct.pack('B', int(self._binary[:8], 2))
            self._binary = self._binary[8:]

    def _convert_to_hex_and_add_padding(self, value, length):
        data = hex(int(value))[2:]
        if data.endswith('L'):
            data = data[:-1]
        return data.rjust(int(length)*2, '0')

    def read_until(self, delimiter=None):
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
            yield hex((struct.unpack('B', d)[0]))[2:].rjust(2, '0')
        self._data = self._data[int(length):]

    def read_binary_from_data(self, length):
        self._binary += "".join(self._read_binary_from_data(int(length)))

    def _read_binary_from_data(self, length):
        for d in self._data[:length]:
            yield d2b(int(str(struct.unpack('B', d)[0])))[1:].rjust(8, '0')
        self._data = self._data[int(length):]

    def read_from_binary(self, length):
        length = int(length)
        if len(self._binary) < length:
            raise Exception("Not enough bits to read")
        value = self._binary[:length]
        self._binary = self._binary[length:]
        return str(int(value,2))

    def add_number_as_tbcd(self, *args):
        nmbr = "".join(args)
        while len(nmbr) > 1:
            self.add_decimal_as_bits(int(nmbr[1]), 4)
            self.add_decimal_as_bits(int(nmbr[0]), 4)
            nmbr = nmbr[2:]
        if nmbr:
            self.add_decimal_as_bits(15, 4)
            self.add_decimal_as_bits(int(nmbr[0]), 4)

    def add_ip_as_hex(self, address):
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

    def read_hex_data(self, length, no_prefix=None):
        a = ""
        if not no_prefix:
            a += "0x"
        return a + "".join(hex(int(self.read_from_data(1)))[2:].rjust(2, '0') for _ in range(int(length)))

    def read_tbcd_coded_numbers_from_data(self, amount):
        length = (int(amount)/2)+(int(amount)%2)
        self.read_binary_from_data(length)
        while len(self._binary) > 8:
            a = self.read_from_binary(4)
            b = self.read_from_binary(4)
            self._tbcd += str(b) + str(a)
        a = self.read_from_binary(4)
        b = self.read_from_binary(4)
        self._tbcd += str(b)
        if int(a) < 10:
            self._tbcd += str(a)

    def read_from_tbcd(self, length):
        number = self._tbcd[:int(length)]
        self._tbcd = self._tbcd[int(length):]
        return number

    def read_ip_from_hex(self):
        return  ".".join(str(self.read_from_data(1)) for _ in range(4))

    def read_string_from_data(self, length):
        string = self._data[:int(length)]
        self._data = self._data[int(length):]
        return string

    def sctp_should_be_supported(self):
        if not Server.SCTP_ENABLED:
            raise AssertionError("SCTP not available on this platform.")
