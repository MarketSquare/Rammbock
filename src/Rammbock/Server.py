#!/usr/bin/python
#-*- coding: iso-8859-15 -*-
#

import socket

try:
    from sctp import sctpsocket_tcp
    SCTP_ENABLED = True
except ImportError:
    SCTP_ENABLED = False

UDP_PACKET_MAX_SIZE = 1024
TCP_PACKET_MAX_SIZE = 1000000
NUMBER_OF_TCP_CONNECTIONS = 1
DEFAULT_NAME = 'server1' 
DEFAULT_IP = '127.0.0.1'



class _Server(object):

    transport_protocol = None

    def __init__(self, server_name=DEFAULT_NAME): 
        self._server_name = server_name
        self._connection = None
        self._client_address = None

    def server_startup(self, ip, port):
        try:
            self._server_socket.bind((ip, int(port)))
        except Exception, e :
            raise IOError("Could not bind socket to ip %s and port %s" % (ip, port), e)

    def close(self):
        self._server_socket.close()

    def server_receives_data(self):
        return self.server_receives_data_and_address()[0]


class UDPServer(_Server):

    def __init__(self, server_name=DEFAULT_NAME):
        _Server.__init__(self, server_name)
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print "*DEBUG* Created UDP server with name %s" % server_name

    def server_receives_data_and_address(self):
        data, self._client_address = self._server_socket.recvfrom(UDP_PACKET_MAX_SIZE)
        return data, self._client_address[0]

    def send_data(self, packet):
        self._server_socket.sendto(packet, self._client_address)


class TCPServer(_Server):

    def __init__(self, server_name=DEFAULT_NAME):
        _Server.__init__(self, server_name)
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print "*DEBUG* Created TCP server with name %s" % server_name

    def server_startup(self, ip, port):
        _Server.server_startup(self, ip, port)
        self._server_socket.listen(NUMBER_OF_TCP_CONNECTIONS)

    def accept_connection(self):
        self._connection, self._client_address = self._server_socket.accept()

    def server_receives_data_and_address(self):
        while True:
            data = self._connection.recv(TCP_PACKET_MAX_SIZE)
            if not data: break
            return data, self._client_address[0]

    def send_data(self, packet):
        self._connection.send(packet)


class SCTPServer(TCPServer):

    def __init__(self, server_name=DEFAULT_NAME):
        if not SCTP_ENABLED:
            raise Exception("SCTP Not enabled")
        else:
            _Server.__init__(self, server_name)
            self._server_socket = sctpsocket_tcp(socket.AF_INET)
            self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print "*DEBUG* Created SCTP server with name %s" % server_name

