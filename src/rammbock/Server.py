#!/usr/bin/python
#-*- coding: iso-8859-15 -*-
#     
import socket
import Interface

UDP_PACKET_MAX_SIZE = 1024
TCP_PACKET_MAX_SIZE = 100000
NUMBER_OF_TCP_CONNECTIONS = 1


class Server(object):
    connection = None
    transport_protocol = None
    
    def __init__(self): 
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def server_startup(self, interface, port, trsprot):
        self.transport_protocol = trsprot
        self.__setup_transport_protocol(trsprot)
        host = str(Interface.get_ip_address(interface))
        if host == '':
            raise IOError('cannot bind server to interface: '+interface)
        print "used host address is: "+host+":"+port
        self._server_socket.bind((host, int(port)))
        if trsprot == 'TCP':
            self._server_socket.listen(NUMBER_OF_TCP_CONNECTIONS)

    def establish_tcp_connection(self):
        self.connection, address = self._server_socket.accept()

    def server_receives_data(self):
        if self.transport_protocol =='UDP':
            data, self._address = self._server_socket.recvfrom(UDP_PACKET_MAX_SIZE)
            return data
        elif self.transport_protocol == 'TCP':
            while 1:
                data = self.connection.recv(TCP_PACKET_MAX_SIZE)
                if not data: break
                return data
        else:
            raise Exception('Unknown Transport Protocol: '+self.transport_protocol)

    def send_data(self, packet):
        if self.transport_protocol == 'UDP':
            self._server_socket.sendto(packet, self._address)
        elif self.transport_protocol == 'TCP':
            self.connection.send(packet)
            
    def close(self):
        self._server_socket.close()

    def __setup_transport_protocol(self, trsprot):
        if trsprot == 'UDP':
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        elif trsprot == 'TCP':
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            raise Exception('wrong transport protocol:'+trsprot )
