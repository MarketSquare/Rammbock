#!/usr/bin/python
#-*- coding: iso-8859-15 -*-

import socket

UDP_PACKET_MAX_SIZE = 1024

class Client(object):

    def establish_connection_to_server(self, host, port, transprt, interface):
        self.__setup_transport_protocol(transprt)
        print 'Connecting to host and port: '+host+':'+port
        print interface
        if interface:
            ownhost = str(rammbocksocket._get_ip_address(self._client_socket, interface))
            self._client_socket.bind((ownhost, int(port)))
        self._client_socket.connect((host, int(port)))

    def send_packet(self, packet): 
        self._client_socket.send(packet)

    def receive_packet_over_udp(self):
        return self._client_socket.recv(UDP_PACKET_MAX_SIZE)     

    def close(self):
        self._client_socket.close()
        
    def __setup_transport_protocol(self, trsprot):
        if trsprot == 'UDP':
            self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        elif trsprot == 'TCP':
            self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            raise Exception('wrong transport protocol:'+trsprot )
