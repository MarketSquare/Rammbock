#!/usr/bin/python
#-*- coding: iso-8859-15 -*-
#

import socket
import Interface

try:
    from sctp import sctpsocket_udp
    SCTP_ENABLED = True
except ImportError:
    SCTP_ENABLED = False

UDP_PACKET_MAX_SIZE = 1024
TCP_PACKET_MAX_SIZE = 1000000
NUMBER_OF_TCP_CONNECTIONS = 1
DEFAULT_NAME = 'server1' 
DEFAULT_IP = '127.0.0.1'



class _Server(object):
    connection = None
    transport_protocol = None

    def __init__(self, server_name=DEFAULT_NAME): 
        self._server_name = server_name

    def server_startup(self, interface, ip, port):
        if Interface.check_interface_for_ip(interface, ip):
            print "used host address is: " + ip + ":" + port
            self._server_socket.bind((ip, int(port)))
        else:
            raise IOError('cannot bind server to interface: ' + interface)

    def close(self):
        self._server_socket.close()


class UDPServer(_Server):

    def __init__(self, server_name=DEFAULT_NAME):
        _Server.__init__(self, server_name)
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def server_receives_data(self):
        data, self._address = self._server_socket.recvfrom(UDP_PACKET_MAX_SIZE)
        return data

    def send_data(self, packet):
        self._server_socket.sendto(packet, self._address)


class TCPServer(_Server):

    def __init__(self, server_name=DEFAULT_NAME):
        _Server.__init__(self, server_name)
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def server_startup(self, interface, ip, port):
        _Server.server_startup(self, interface, ip, port)
        self._server_socket.listen(NUMBER_OF_TCP_CONNECTIONS)

    def accept_connection(self):
        self.connection, _ = self._server_socket.accept()

    def server_receives_data(self):
        while 1:
            data = self.connection.recv(TCP_PACKET_MAX_SIZE)
            if not data: break
            return data

    def send_data(self, packet):
        self.connection.send(packet)


class SCTPServer(UDPServer):


    def __init__(self, server_name=DEFAULT_NAME):
        if not SCTP_ENABLED:
            raise Exception("SCTP Not enabled")
        else:
            _Server.__init__(self, server_name)
            self._server_socket = sctpsocket_udp(socket.AF_INET)

