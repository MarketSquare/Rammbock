#!/usr/bin/python
#-*- coding: iso-8859-15 -*-

import socket, IN

UDP_PACKET_MAX_SIZE = 1024

class Client(object):

    def __init__(self, interfaces):
        self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._interfaces = interfaces
                     
    def establish_connection_to_server(self, host, port, ifalias):
        ifname = str(self._interfaces[ifalias].ifname)
        print "Network interface used by client: %s" % ifname
        self._client_socket.setsockopt(socket.SOL_SOCKET, IN.SO_BINDTODEVICE, ifname + '\0')
        self._client_socket.connect((host, int(port)))

    def send_packet_over_udp(self, packet): 
        self._client_socket.send(packet) # send test string

    def receive_packet_over_udp(self):
        return self._client_socket.recv(UDP_PACKET_MAX_SIZE)     

    def close(self):
        self._client_socket.close()