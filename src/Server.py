#!/usr/bin/python
#-*- coding: iso-8859-15 -*-
     
import socket
import sys
import time

UDP_PACKET_MAX_SIZE = 1024

class Server(object):
     
     def __init__(self, interfaces): 
          self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
          self._interfaces = interfaces
     
     def server_startup(self, interface, port):
          host = str(self._interfaces[interface].ifIpAddress)
          print "used host address is: "+host+":"+port
          self._server_socket.bind((host, int(port)))
     
     def receive_packet_over_udp(self):
          data, self._address = self._server_socket.recvfrom(UDP_PACKET_MAX_SIZE)
          return data
     
     def send_packet_over_udp(self, packet):
          self._server_socket.sendto(packet, self._address)
     
     def close_server(self):
          self._server_socket.close()
