#!/usr/bin/python
#-*- coding: iso-8859-15 -*-
     
import socket
import sys
import time

UDP_PACKET_MAX_SIZE = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

class Server:
     
     def server_startup(self, interface, port):
          host = str(self.interfaces[interface].ifIpAddress)
          print "used host address is: "+host+":"+port
          s.bind((host, int(port)))
     
     def receive_packet_over_udp(self):
          return s.recv(UDP_PACKET_MAX_SIZE)    
     
     def close_server(self):
          s.close()
          del self     