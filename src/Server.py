#!/usr/bin/python
#-*- coding: iso-8859-15 -*-
     
import socket
import sys
import time

UDP_PACKET_MAX_SIZE = 1024

class Server(object):
     
     def __init__(self, interfaces): 
          self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
          self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
          self._interfaces = interfaces
     
     def server_startup(self, interface, port):
          host = str(self._interfaces[interface].ifIpAddress)
          print "used host address is: "+host+":"+port
          self._server_socket.bind((host, int(port)))
     
     def receive_packet_over_udp(self):
          return self._server_socket.recv(UDP_PACKET_MAX_SIZE)    
     
     def close_server(self):
          #self._server_socket.shutdown(socket.SHUT_RD)
          self._server_socket.close()
          self._server_socket = None
          print 'closing server'
