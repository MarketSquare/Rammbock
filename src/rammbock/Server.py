#!/usr/bin/python
#-*- coding: iso-8859-15 -*-
#     
import socket
import rammbocksocket
CONNECTION = None

UDP_PACKET_MAX_SIZE = 1024
TCP_PACKET_MAX_SIZE = 100000
NUMBER_OF_TCP_CONNECTIONS = 1

class Server(object):
    connection = None

    def server_startup(self, interface, port, trsprot):
        self.__setup_transport_protocol(trsprot)
        try:
            host = str(rammbocksocket._get_ip_address(self._server_socket, interface))
        except IOError:
            raise IOError('cannot bind server to interface: '+interface)
        print "used host address is: "+host+":"+port
        self._server_socket.bind((host, int(port)))
        if trsprot == 'TCP':
            self._server_socket.listen(NUMBER_OF_TCP_CONNECTIONS)

    def establish_tcp_connection(self):
        self.connection, address = self._server_socket.accept()

    def receive_packet_over_udp(self):
        data, self._address = self._server_socket.recvfrom(UDP_PACKET_MAX_SIZE)
        return data

    def receive_packet_over_tcp(self):
        data = self.connection.recv(TCP_PACKET_MAX_SIZE)
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
