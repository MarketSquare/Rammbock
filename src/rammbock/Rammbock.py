from Client import Client
from Server import Server

class Rammbock(object):

    def __init__(self):
        self._client = Client()
        self._server = Server()

    def start_server(self, nwinterface, port):
        self._server.server_startup(nwinterface, port)

    def connect_to_server(self, host, port, ifname = False):
        self._client.establish_connection_to_server(host, port, ifname)

    def close_server(self):
        self._server.close()

    def close_client(self):
        self._client.close()

    def client_send_packet_over_udp(self, packet): 
        self._client.send_packet_over_udp(packet)

    def server_receive_packet_over_udp(self):
        return self._server.receive_packet_over_udp()

    def server_send_packet_over_udp(self, packet): 
        self._server.send_packet_over_udp(packet)

    def client_receive_packet_over_udp(self):
        return self._client.receive_packet_over_udp()
