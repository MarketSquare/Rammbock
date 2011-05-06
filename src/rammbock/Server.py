#!/usr/bin/python
#-*- coding: iso-8859-15 -*-
#     
import socket
import fcntl
import struct

UDP_PACKET_MAX_SIZE = 1024

class Server(object):

    def __init__(self): 
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def server_startup(self, interface, port):
        print interface
        host = str(self.__get_ip_address(interface))
        print "used host address is: "+host+":"+port
        self._server_socket.bind((host, int(port)))

    def receive_packet_over_udp(self):
        data, self._address = self._server_socket.recvfrom(UDP_PACKET_MAX_SIZE)
        return data

    def send_packet_over_udp(self, packet):
        self._server_socket.sendto(packet, self._address)

    def close(self):
        self._server_socket.close()

    def __get_ip_address(self, ifname):
        ifname=str(ifname)
        return socket.inet_ntoa(fcntl.ioctl(
            self._server_socket.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])
        