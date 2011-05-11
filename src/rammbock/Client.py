#!/usr/bin/python
#-*- coding: iso-8859-15 -*-

import socket
import Interface

UDP_PACKET_MAX_SIZE = 1024
TCP_PACKET_MAX_SIZE = 100000


class _Client(object):
    transport_protocol = None
    def establish_connection_to_server(self, host, port, interface):
        print 'Connecting to host and port: '+host+':'+port
        print interface
        if interface:
            ownhost = str(Interface.get_ip_address(interface))
            self._client_socket.bind((ownhost, int(port)))
        self._client_socket.connect((host, int(port)))

    def send_packet(self, packet): 
        self._client_socket.send(packet)

    def receive_data(self):
        raise Exception('Unknown Transport Protocol: '+self.transport_protocol)

    def close(self):
        self._client_socket.close()


class UDPClient(_Client):
    transport_protocol = 'UDP'
    def __init__(self):
        self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def receive_data(self):
        return self._client_socket.recv(UDP_PACKET_MAX_SIZE)

class TCPClient(_Client):
    transport_protocol = 'TCP'
    def __init__(self):
        self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def receive_data(self):
        while 1:
            data = self._client_socket.recv(TCP_PACKET_MAX_SIZE)
            if not data: break
            return data
