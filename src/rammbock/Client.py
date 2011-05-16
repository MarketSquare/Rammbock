#!/usr/bin/python
#-*- coding: iso-8859-15 -*-

import socket
import Interface

UDP_PACKET_MAX_SIZE = 1024
TCP_PACKET_MAX_SIZE = 1000000
DEFAULT_NAME = 'client1'


class _Client(object):

    def __init__(self, clientname=DEFAULT_NAME):
        self._name = clientname


    def establish_connection_to_server(self, host, port, interface):
        print 'Connecting to host and port: '+host+':'+port
        print interface
        if interface:
            ownhost = str(Interface.get_ip_address(interface))
            self._client_socket.bind((ownhost, int(port)))
        self._client_socket.connect((host, int(port)))

    def send_packet(self, packet): 
        self._client_socket.send(packet)

    def close(self):
        self._client_socket.close()


class UDPClient(_Client):
    def __init__(self, name=DEFAULT_NAME):
        _Client.__init__(self, name)
        self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def receive_data(self):
        return self._client_socket.recv(UDP_PACKET_MAX_SIZE)


class TCPClient(_Client):
    def __init__(self, name=DEFAULT_NAME):
        _Client.__init__(self, name)
        self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def receive_data(self):
        while 1:
            data = self._client_socket.recv(TCP_PACKET_MAX_SIZE)
            if not data: break
            return data
