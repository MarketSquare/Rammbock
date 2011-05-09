#!/usr/bin/python
#-*- coding: iso-8859-15 -*-
#     
import socket
import rammbocksocket

UDP_PACKET_MAX_SIZE = 1024

class Server(object):

    def server_startup(self, interface, port, trsprot):
        self.__setup_transport_protocol(trsprot)
        try:
            host = str(rammbocksocket._get_ip_address(self._server_socket, interface))
        except IOError:
            raise IOError('cannot bind server to interface: '+interface)
        print "used host address is: "+host+":"+port
        self._server_socket.bind((host, int(port)))

    def receive_packet_over_udp(self):
        data, self._address = self._server_socket.recvfrom(UDP_PACKET_MAX_SIZE)
        return data

    def send_packet_over_udp(self, packet):
        self._server_socket.sendto(packet, self._address)

    def close(self):
        self._server_socket.close()

    def __setup_transport_protocol(self, trsprot):
        if trsprot == 'UDP':
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        elif trsprot == 'TCP':
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            raise Exception('wrong transport protocol:'+trsprot )
