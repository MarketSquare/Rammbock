from Client import UDPClient, TCPClient
from Server import UDPServer, TCPServer
import Server
import Client
import Encode
from rammbock.Message import Message


class Rammbock(object):

    def __init__(self):
        self.message = None
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

    def client_sends_data(self, packet, name=Client.DEFAULT_NAME): 
        self._clients[name].send_packet(packet)

    def server_receives_data(self, name=Server.DEFAULT_NAME):
        return self._servers[name].server_receives_data()

    def server_receives_message(self):
        message = self.server_receives_data(self)
        Decoder.decode_data_to_object(message)

    def client_receives_data(self, name=Client.DEFAULT_NAME):
        return self._clients[name].receive_data()

    def server_sends_data(self, packet, name=Server.DEFAULT_NAME): 
        self._servers[name].send_data(packet)

    def client_sends_message(self, client_name=Client.DEFAULT_NAME, server_name=Server.DEFAULT_NAME):
        data_bin = Encode.encode_to_bin(self.message)
        self.client_sends_data(data_bin)

    def create_message(self):
        self.message = Message()

    def get_header_field(self, name):
        return (x for _, x in self.message.header if _ == name).next()

    def get_information_element(self, name):
        return (x for _, x in self.message.ie if _ == name).next()

    def add_information_element(self, name, value=None):
        self.message.ie.append((name, value))

    def modify_information_element(self, name, value):
        self.message.ie[self._id_to_name(self.message.ie, name)] = (name,value)

    def add_header(self, name, value):
        self.message.header.append((name, value))

    def modify_header_field(self, name, value):
        self.message.header[self._id_to_name(self.message.header, name)] = (name,value)

    def delete_information_element(self, name):
        del self.message.ie[self._id_to_name(self.message.ie, name)]

    def delete_header_field(self, name):
        del self.message.header[self._id_to_name(self.message.header, name)]

    def _id_to_name(self, which, name):
        return (x for x, i in enumerate(which) if i[0] == name).next()
