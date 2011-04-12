#!/usr/bin/python
#-*- coding: iso-8859-15 -*-
     
import socket
import sys

UDP_PACKET_MAX_SIZE = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

class Server:
     
     def server_startup(self, interface, port, host=''):
          s.bind((host, int(port)))
     
     def receive_packet_over_udp(self):
          return s.recv(UDP_PACKET_MAX_SIZE)    
          s.close()         