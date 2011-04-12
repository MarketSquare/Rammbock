#!/usr/bin/python
#-*- coding: iso-8859-15 -*-

import socket
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


class Client:

     def establish_connection_to_server(self, host, port):
           s.connect((host, int(port)))


     def send_packet_over_udp(self, packet): 
          s.send(packet) # send test string

     def close_client(self):
          s.close()     
