from Client import UDPClient, TCPClient
from Server import UDPServer, TCPServer
import Server
import Client
import struct


class Rammbock(object):

    IE_NOT_FOUND = "Information Element does not exist: '%s'"
    HEADER_NOT_FOUND = "Header does not exist: '%s'"
    BINARY_NOT_FOUND = "Header does not exist: '%s'"

    def __init__(self):
        self.data = ""
        self._servers = {}
        self._clients = {}

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
            self._clients[name].send_packet(self.data)

    def server_receives_data(self, name=Server.DEFAULT_NAME):
        self.data = self._servers[name].server_receives_data()
        return self.data

    def client_receives_data(self, name=Client.DEFAULT_NAME):
        self.data = self._clients[name].receive_data()
        return self.data

    def server_sends_data(self, packet=None, name=Server.DEFAULT_NAME): 
        if packet:
            self._servers[name].send_data(packet)
        else:
            self._servers[name].send_data(self.data)

    def create_message(self):
        self.data = ""

    def add_string(self, value):
        self.data += str(value)

    def add_decimal_as_binary(self, value, length):
        data = hex(int(value))[2:]
        data = data.rjust(int(length)*2, '0')
        while(len(data) > 0):
                self.data += struct.pack('B', int(data[0:2],16))
                data = data[2:]

    def read_until(self, delimiter=None):
        if delimiter:
            i,_,self.data = self.data.partition(delimiter)
            return i
        return self.data

    def read_from_data(self, length):
        message_temp = ""
        temp = list(self.data)
        temp.reverse()
        for d in range(0, int(length)):
            message_temp += str(struct.unpack('B', temp.pop())[0])
        temp.reverse()
        self.data = temp
        return str(int(message_temp))
