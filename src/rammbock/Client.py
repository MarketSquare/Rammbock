#!/usr/bin/python
#-*- coding: iso-8859-15 -*-

import socket
import Interface

UDP_PACKET_MAX_SIZE = 1024
TCP_PACKET_MAX_SIZE = 100000

class Client(object):

    def establish_connection_to_server(self, host, port, transprt, interface):
        self.__setup_transport_protocol(transprt)
        print 'Connecting to host and port: '+host+':'+port
        print interface
        if interface:
            ownhost = str(Interface.get_ip_address(interface))
            self._client_socket.bind((ownhost, int(port)))
        self._client_socket.connect((host, int(port)))

    def send_packet(self, packet): 
        self._client_socket.send(packet)

    def receive_packet_over_udp(self):
        return self._client_socket.recv(UDP_PACKET_MAX_SIZE)     

    def receive_packet_over_tcp(self):
        i = 0
        while(1):
            data = self._client_socket.recv(TCP_PACKET_MAX_SIZE) # read up to 1000000 bytes
            i += 1
            if (i < 5): # look only at the first part of the message
                print data
            if not data: # if end of data, leave loop
                break
            return data

    def close(self):
        self._client_socket.close()
        
    def __setup_transport_protocol(self, trsprot):
        if trsprot == 'UDP':
            self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        elif trsprot == 'TCP':
            self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            raise Exception('wrong transport protocol:'+trsprot )

    
