#!/usr/bin/python
#-*- coding: iso-8859-15 -*-
#     
import socket
import Interface

UDP_PACKET_MAX_SIZE = 1024
TCP_PACKET_MAX_SIZE = 1000000
NUMBER_OF_TCP_CONNECTIONS = 1
DEFAULT_SERVER_NAME = 'server1' 

class _Server(object):
    connection = None
    transport_protocol = None
    
    def __init__(self, servername=DEFAULT_SERVER_NAME): 
        self._servername = servername
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def server_startup(self, interface, port):
        host = str(Interface.get_ip_address(interface))
        if host == '':
            raise IOError('cannot bind server to interface: '+interface)
        print "used host address is: "+host+":"+port
        self._server_socket.bind((host, int(port)))

    def close(self):
        self._server_socket.close()


class UDPServer(_Server):

    def __init__(self, servername=DEFAULT_SERVER_NAME):
        _Server.__init__(self, servername)
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def server_receives_data(self):
        data, self._address = self._server_socket.recvfrom(UDP_PACKET_MAX_SIZE)
        return data

    def send_data(self, packet):
        self._server_socket.sendto(packet, self._address)


class TCPServer(_Server):

    def __init__(self, servername=DEFAULT_SERVER_NAME):
        _Server.__init__(self, servername)
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


    def server_startup(self, interface, port):
        _Server.server_startup(self, interface, port)
        self._server_socket.listen(NUMBER_OF_TCP_CONNECTIONS)

    def accept_connection(self):
        self.connection, _ = self._server_socket.accept()

    def server_receives_data(self):
        while 1:
            data = self.connection.recv(TCP_PACKET_MAX_SIZE)
            if not data: break
            return data

    def send_data(self, packet):
        self.connection.send(packet)
