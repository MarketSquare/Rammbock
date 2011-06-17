from Client import UDPClient, TCPClient
from Server import UDPServer, TCPServer
import Server
import Client
import Encoder
import Decoder

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

    def client_sends_message(self):
        data_bin = Encoder.object2string(self.message)
        self.client_sends_data(data_bin)

    def server_receives_data(self, name=Server.DEFAULT_NAME):
        return self._servers[name].server_receives_data()

    def server_receives_message(self, name=Server.DEFAULT_NAME):
        msg = self.server_receives_data(name)
        Decoder.string2object(self.message, msg)

    def client_receives_data(self, name=Client.DEFAULT_NAME):
        return self._clients[name].receive_data()

    def client_receives_message(self, name=Client.DEFAULT_NAME):
        msg = self.client_receives_data(name)
        Decoder.string2object(self.message, msg)

    def server_sends_data(self, packet, name=Server.DEFAULT_NAME): 
        self._servers[name].send_data(packet)

    def server_sends_message(self):
        data_bin = Encoder.object2string(self.message)
        self.server_sends_data(data_bin)

    def create_message(self, protocol = None, version = None, message = None):
        self.message = Message(protocol, version, message)

    def get_header(self, name):
        return self._first_by_name(name, self.message.header)

    def _first_by_name(self, name, collection):
        return (item for item_name, item in collection if item_name == name).next()

    def get_information_element(self, name):
        return self._first_by_name(name, self.message.ie)

    def add_information_element(self, name, value=None):
        self.message.ie.append((name, value))

    def add_information_element_schema(self, name):
        self.message.ie += name
        self.message.message += 'IE'


    def modify_information_element(self, name, value):
        self.message.ie[self._id_to_name(self.message.ie, name)] = (name,value)

    def add_header(self, name, value = None):
        if value == None:
            self.message.header.append((name))
        else:
            self.message.header.append((name, value))

    def add_header_schema(self, name):
        self.message.header += [name]
        self.message.message += 'Header'

    def modify_header_field(self, name, value):
        self.message.header[self._id_to_name(self.message.header, name)] = (name,value)

    def delete_information_element(self, name):
        del self.message.ie[self._id_to_name(self.message.ie, name)]

    def delete_header_field(self, name):
        del self.message.header[self._id_to_name(self.message.header, name)]

    def _id_to_name(self, which, name):
        return (x for x, i in enumerate(which) if i[0] == name).next()
