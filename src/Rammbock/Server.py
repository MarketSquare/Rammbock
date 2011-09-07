#  Copyright 2011 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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

    def __init__(self, server_name=DEFAULT_NAME): 
        self._server_name = server_name
        self._client_address = None

    def server_startup(self, ip, port):
        try:
            self._server_socket.bind((ip, int(port)))
        except Exception, e :
            raise IOError("Could not bind socket to ip %s and port %s" % (ip, port), e)

    def close(self):
        self._server_socket.close()

    def server_receives_data(self, connection_alias=None):
        return self.server_receives_data_and_address(connection_alias)[0]


class UDPServer(_Server):

    def __init__(self, server_name=DEFAULT_NAME):
        _Server.__init__(self, server_name)
        self._latest_client_address = None
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print "*DEBUG* Created UDP server with name %s" % server_name

    def server_receives_data_and_address(self, connection_alias=None):
        if connection_alias:
            raise Exception("UDP is connectionless protocol")
        data, self._latest_client_address = self._server_socket.recvfrom(UDP_PACKET_MAX_SIZE)
        return (data,)+self._latest_client_address

    def send_data(self, packet, ip=None, port=None):
        if not ip or not port:
            ip,port = self._latest_client_address
        self._server_socket.sendto(packet, (ip,port))


class TCPServer(_Server):

    def __init__(self, server_name=DEFAULT_NAME):
        _Server.__init__(self, server_name)
        self._connections = {}
        self._server_socket = self._init_socket()
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def _init_socket(self):
        print "*DEBUG* Created TCP server with name %s" % self._server_name
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def server_startup(self, ip, port):
        _Server.server_startup(self, ip, port)
        self._server_socket.listen(NUMBER_OF_TCP_CONNECTIONS)

    def accept_connection(self, alias=None):
        connection, client_address = self._server_socket.accept()
        self._connections[alias] = (connection, client_address)
        return client_address

    def server_receives_data_and_address(self, connection_alias=None):
        while True:
            data = self._get_connection(connection_alias).recv(TCP_PACKET_MAX_SIZE)
            if not data: break
            return (data,)+self._get_connection_address(connection_alias)

    def send_data(self, packet, connection_alias=None):
        self._get_connection(connection_alias).send(packet)

    def _get_connection(self, connection_alias):
        return self._get_connection_and_address(connection_alias)[0]

    def _get_connection_address(self, connection_alias):
        return self._get_connection_and_address(connection_alias)[1]

    def _get_connection_and_address(self, connection_alias):
        if not connection_alias:
            connection_alias = self._connections.keys()[0]
        return self._connections[connection_alias]


class SCTPServer(TCPServer):

    def __init__(self, server_name=DEFAULT_NAME):
        if not SCTP_ENABLED:
            raise Exception("SCTP Not enabled")
        TCPServer.__init__(self, server_name)

    def _init_socket(self):
        print "*DEBUG* Created SCTP server with name %s" % self._server_name
        return sctpsocket_tcp(socket.AF_INET)
