#!/usr/bin/python
#-*- coding: iso-8859-15 -*-

# Socket-server

import socket
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

class Server:
     
     def server_startup(self, interface, port, host=''):
          s.bind((host, int(port)))
     
     def receive_packet_over_udp(self):
          return s.recv(1024)    
          conn.close()
          