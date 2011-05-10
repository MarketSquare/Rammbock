#!/usr/bin/python
#-*- coding: iso-8859-15 -*-

import socket
import Interface

UDP_PACKET_MAX_SIZE = 1024
TCP_PACKET_MAX_SIZE = 100000


class Client(object):
    transport_protocol = None
    
    def establish_connection_to_server(self, host, port, transprt, interface):
        self._setup_transport_protocol(transprt)
        print 'Connecting to host and port: '+host+':'+port
        print interface
        if interface:
            ownhost = str(Interface.get_ip_address(interface))
            self._client_socket.bind((ownhost, int(port)))
        self._client_socket.connect((host, int(port)))

    def send_packet(self, packet): 
        self._client_socket.send(packet)

    def receive_data(self):
        if self.transport_protocol == 'UDP':
            return self._client_socket.recv(UDP_PACKET_MAX_SIZE)     
        if self.transport_protocol == 'TCP':
            while 1:
                data = self._client_socket.recv(TCP_PACKET_MAX_SIZE)
                if not data: break
                return data
        else:
            raise Exception('Unknown Transport Protocol: '+self.transport_protocol)

    def close(self):
        self._client_socket.close()
        
    def _setup_transport_protocol(self, trsprot):
        self.transport_protocol = trsprot
        if trsprot == 'UDP':
            self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        elif trsprot == 'TCP':
            self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            raise Exception('wrong transport protocol:'+trsprot )
