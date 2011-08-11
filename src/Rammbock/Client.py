#!/usr/bin/python
#-*- coding: iso-8859-15 -*-

import socket

try:
    from sctp import sctpsocket_tcp
    SCTP_ENABLED = True
except ImportError:
    SCTP_ENABLED = False

UDP_PACKET_MAX_SIZE = 1024
TCP_PACKET_MAX_SIZE = 1000000
DEFAULT_NAME = 'client1'


class _Client(object):

    def __init__(self, client_name=DEFAULT_NAME, ip=None):
        self._name = client_name
        self._init_socket()
        if ip:
            self._client_socket.bind((ip, 0))

    def establish_connection_to_server(self, host, port, interface):
        print 'Connecting to host and port: '+host+':'+port
        self._client_socket.connect((host, int(port)))

    def send_packet(self, packet):
        self._client_socket.send(packet)

    def close(self):
        self._client_socket.close()


class UDPClient(_Client):

    def _init_socket(self):
        self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def receive_data(self):
        return self._client_socket.recv(UDP_PACKET_MAX_SIZE)


class TCPClient(_Client):

    def _init_socket(self):
        self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def receive_data(self):
        while 1:
            data = self._client_socket.recv(TCP_PACKET_MAX_SIZE)
            if not data: break
            return data


class SCTPClient(TCPClient):

    def _init_socket(self):
        if not SCTP_ENABLED:
            raise Exception("SCTP Not enabled")
        else:
            self._client_socket = sctpsocket_tcp(socket.AF_INET)
            self._client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
