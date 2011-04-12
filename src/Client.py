#!/usr/bin/python
#-*- coding: iso-8859-15 -*-

import socket
import sys

class Client:

def estabslih_connection_to_server(self, host, port):
     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
     s.connect((host, port))


def send_packet_over_udp(self, packet): 
     s.send(packet) # send test string
     s.close()     
