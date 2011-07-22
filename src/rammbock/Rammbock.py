from Client import UDPClient, TCPClient
from Server import UDPServer, TCPServer
import Server
import Client
import struct


d2b = lambda d: (not isinstance(d,int) or (d==0)) and '0' \
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

    def start_udp_server(self, nwinterface, port, ip=Server.DEFAULT_IP, name=Server.DEFAULT_NAME):
        self._servers[name] = UDPServer(name)
        self._servers[name].server_startup(nwinterface, ip, port)

    def start_tcp_server(self, nwinterface, port, ip=Server.DEFAULT_IP, name=Server.DEFAULT_NAME):
        self._servers[name] = TCPServer(name)
        self._servers[name].server_startup(nwinterface, ip, port)

    def check_server_status(self, name=Server.DEFAULT_NAME):
        return name in self._servers

    def check_client_status(self, name=Client.DEFAULT_NAME):
        return name in self._clients

    def connect_to_udp_server(self, host, port, ifname = False, client=Client.DEFAULT_NAME):
        self._clients[client].establish_connection_to_server(host, port, ifname)

    def connect_to_tcp_server(self, host, port, ifname = False, client=Client.DEFAULT_NAME):
        self._clients[client].establish_connection_to_server(host, port, ifname)

    def accept_tcp_connection(self, server=Server.DEFAULT_NAME):
        self._servers[server].accept_connection()

    def close_server(self, name=Server.DEFAULT_NAME):
        self._servers[name].close()
        del self._servers[name]

    def create_udp_client(self, name=Client.DEFAULT_NAME):
        self._clients[name] = UDPClient(name)

    def create_tcp_client(self, name=Client.DEFAULT_NAME):
        self._clients[name] = TCPClient(name)

    def close_client(self, name=Client.DEFAULT_NAME):
        self._clients[name].close()
        del self._clients[name] 

    def client_sends_data(self, packet=None, name=Client.DEFAULT_NAME):
        if packet:
            self._clients[name].send_packet(packet)
        else:
            self._clients[name].send_packet(self._data)

    def server_receives_data(self, name=Server.DEFAULT_NAME):
        self._data = self._servers[name].server_receives_data()
        return self._data

    def client_receives_data(self, name=Client.DEFAULT_NAME):
        self._data = self._clients[name].receive_data()
        return self._data

    def server_sends_data(self, packet=None, name=Server.DEFAULT_NAME): 
        if packet:
            self._servers[name].send_data(packet)
        else:
            self._servers[name].send_data(self._data)

    def create_message(self):
        self._data = ""

    def add_string(self, value, length=None):
        if not length:
            length = len(value)
        self._data += str(value).rjust(int(length), '\0')

    def add_decimal_as_octets(self, value, length):
        data = self._convert_to_hex_and_add_padding(value, length)
        if len(data) > int(length)*2:
            raise Exception("Value is too big for length")
        while(len(data) > 0):
                self._data += struct.pack('B', int(data[0:2],16))
                data = data[2:]

    def add_decimal_as_bits(self, value, length):
        data = d2b(int(value))[1:].rjust(int(length), '0')
        if len(data) > int(length):
            raise Exception("Value is too big for length")
        self._binary += data
        while len(self._binary) >= 8:
            self._data += struct.pack('B', int(self._binary[:8],2))
            self._binary = self._binary[8:]

    def _convert_to_hex_and_add_padding(self, value, length):
        data = hex(int(value))[2:]
        if data[-1] == 'L':
            data = data[:-1]
        data = data.rjust(int(length)*2, '0')
        return data

    def read_until(self, delimiter=None):
        if delimiter:
            i,_,self._data = self._data.partition(delimiter)
            return i
        return self._data

    def read_from_data(self, length):
        length = int(length)
        message = ""
        for d in self._data[:length]:
            message += str(struct.unpack('B', d)[0])
        self._data = self._data[length:]
        return str(int(message))

    def read_to_binary_from_data(self, length):
        length = int(length)
        for d in self._data[:length]:
            self._binary += d2b(int(str(struct.unpack('B', d)[0])))[1:].rjust(8,'0')
        self._data = self._data[length:]

    def read_from_binary(self, length):
        length = int(length)
        value = self._binary[:length]
        self._binary = self._binary[length:]
        return str(int(value,2))

    def add_number_as_tbcd(self, *args):
        nmbr = "".join(args)
        temp = ""
        while len(nmbr) > 1:
            temp += nmbr[1]
            temp += nmbr[0]
            nmbr = nmbr[2:]
        for a in temp:
            self.add_decimal_as_bits(int(a), 4)
        if nmbr:
            self.add_decimal_as_bits(int(15), 4)
            self.add_decimal_as_bits(int(nmbr[0]),4)
