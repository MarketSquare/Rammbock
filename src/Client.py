#!/usr/bin/python
#-*- coding: iso-8859-15 -*-

import socket
import sys

class Client(object):

     def __init__(self):
          self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

     def establish_connection_to_server(self, host, port):
          self._client_socket.connect((host, int(port)))

     def send_packet_over_udp(self, packet): 
          self._client_socket.send(packet) # send test string

     def close_client(self):
          self._client_socket.close()
