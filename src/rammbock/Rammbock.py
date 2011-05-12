from Client import UDPClient, TCPClient
from Server import UDPServer, TCPServer

class Rammbock(object):

    def start_udp_server(self, nwinterface, port):
        self._server = UDPServer()
        self._server.server_startup(nwinterface, port)

    def start_tcp_server(self, nwinterface, port):
        self._server = TCPServer()
        self._server.server_startup(nwinterface, port)

    def connect_to_udp_server(self, host, port, ifname = False):
        self._client = UDPClient()
        self._client.establish_connection_to_server(host, port, ifname)

    def connect_to_tcp_server(self, host, port, ifname = False):
        self._client = TCPClient()
        self._client.establish_connection_to_server(host, port, ifname)

    def accept_tcp_connection(self):
        self._server.accept_connection()
    
    def close_server(self):
        self._server.close()

    def close_client(self):
        self._client.close()

    def client_sends_data(self, packet): 
        self._client.send_packet(packet)

    def server_receives_data(self):
        return self._server.server_receives_data()

    def client_receives_data(self):
        return self._client.receive_data()

    def server_sends_data(self, packet): 
        self._server.send_data(packet)
