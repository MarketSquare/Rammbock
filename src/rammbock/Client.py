#!/usr/bin/python
#-*- coding: iso-8859-15 -*-

import socket
import rammbocksocket

UDP_PACKET_MAX_SIZE = 1024

class Client(object):

    def __init__(self):
        self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def establish_connection_to_server(self, host, port, transprt, interface):
        print 'Connecting to host and port: '+host+':'+port
        print interface
        if interface:
            ownhost = str(rammbocksocket._get_ip_address(self._client_socket, interface))
            self._client_socket.bind((ownhost, int(port)))
        self._client_socket.connect((host, int(port)))

    def send_packet_over_udp(self, packet): 
        self._client_socket.send(packet) # send test string

    def receive_packet_over_udp(self):
        return self._client_socket.recv(UDP_PACKET_MAX_SIZE)     

    def close(self):
        self._client_socket.close()