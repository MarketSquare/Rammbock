#!/usr/bin/python
#-*- coding: iso-8859-15 -*-
#     
import socket
import Interface

UDP_PACKET_MAX_SIZE = 1024
TCP_PACKET_MAX_SIZE = 100000
NUMBER_OF_TCP_CONNECTIONS = 1


class _Server(object):
    connection = None
    transport_protocol = None
    
    def __init__(self): 
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def server_startup(self, interface, port):
        self._setup_transport_protocol(self.transport_protocol)
        host = str(Interface.get_ip_address(interface))
        if host == '':
            raise IOError('cannot bind server to interface: '+interface)
        print "used host address is: "+host+":"+port
        self._server_socket.bind((host, int(port)))

    def establish_tcp_connection(self):
        self.connection, _ = self._server_socket.accept()

    def server_receives_data(self):
        raise Exception('Unknown Transport Protocol: '+self.transport_protocol)

    def send_data(self, packet):
        raise Exception('wrong transport protocol:'+self.transport_protocol )

    def close(self):
        self._server_socket.close()

    def _setup_transport_protocol(self, trsprot):
        if trsprot == 'UDP':
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        elif trsprot == 'TCP':
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            raise Exception('wrong transport protocol:'+trsprot )

class UDPServer(_Server):
    transport_protocol = 'UDP'

    def server_receives_data(self):
        data, self._address = self._server_socket.recvfrom(UDP_PACKET_MAX_SIZE)
        return data
    
    def send_data(self, packet):
        self._server_socket.sendto(packet, self._address)

class TCPServer(_Server):
    transport_protocol = 'TCP'

    def server_startup(self, interface, port):
        _Server.server_startup(self, interface, port)
        self._server_socket.listen(NUMBER_OF_TCP_CONNECTIONS)

    def server_receives_data(self):
        while 1:
            data = self.connection.recv(TCP_PACKET_MAX_SIZE)
            if not data: break
            return data
    
    def send_data(self, packet):
        self.connection.send(packet)
