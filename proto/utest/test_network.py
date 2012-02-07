import unittest
import sys, os
import time
import socket
sys.path.append(os.path.join(os.path.dirname(__file__), '..','src'))
from Network import UDPServer, TCPServer, UDPClient, TCPClient

LOCAL_IP = '127.0.0.1'
SERVER_PORT = 12345
SERVER_PORT_2 = 12346
CLIENT_PORT = 54321
CLIENT_PORT_2 = 64321

class TestNetwork(unittest.TestCase):

    def setUp(self):
        self.sockets = []

    def tearDown(self, *args, **kwargs):
        for sock in self.sockets:
            sock.close()
        return unittest.TestCase.tearDown(self, *args, **kwargs)

    def test_send_and_receive_udp(self):
        server, client = self._udp_server_and_client(SERVER_PORT, CLIENT_PORT)
        client.send('foofaa')
        msg = server.receive()
        self.assertEquals('foofaa', msg)

    def test_setting_client_default_timeout(self):
        _, client = self._udp_server_and_client(SERVER_PORT, CLIENT_PORT, timeout=0.1)
        start_time = time.time()
        self.assertRaises(socket.timeout, client.receive)
        self.assertTrue(time.time()-0.5 < start_time)

    def test_overriding_client_read_timeout(self):
        _, client = self._udp_server_and_client(SERVER_PORT, CLIENT_PORT, timeout=5)
        start_time = time.time()
        self.assertRaises(socket.timeout, client.receive, 0.1)
        self.assertTrue(time.time()-0.5 < start_time)

    def test_overriding_server_read_timeout(self):
        server, _ = self._udp_server_and_client(SERVER_PORT, CLIENT_PORT, timeout=5)
        start_time = time.time()
        self.assertRaises(socket.timeout, server.receive, 0.1)
        self.assertTrue(time.time()-0.5 < start_time)

    def test_setting_server_default_timeout(self):
        server, _ = self._udp_server_and_client(SERVER_PORT, CLIENT_PORT, timeout=0.1)
        start_time = time.time()
        self.assertRaises(socket.timeout, server.receive)
        self.assertTrue(time.time()-0.5 < start_time)

    # TODO: Test for blocking mode

    def test_server_send_udp(self):
        server, client = self._udp_server_and_client(SERVER_PORT, CLIENT_PORT)
        server.send_to('foofaa', LOCAL_IP, CLIENT_PORT)
        msg = client.receive()
        self.assertEquals('foofaa', msg)

    def test_server_send_tcp(self):
        server, client = self._tcp_server_and_client(SERVER_PORT, CLIENT_PORT)
        server.accept_connection()
        server.send('foofaa')
        msg = client.receive()
        self.assertEquals('foofaa', msg)

    def test_send_and_receive_tcp(self):
        server, client = self._tcp_server_and_client(SERVER_PORT, CLIENT_PORT)
        client.send('foofaa')
        server.accept_connection()
        msg = server.receive()
        self.assertEquals('foofaa', msg)

    def _udp_server_and_client(self, server_port, client_port, timeout=None):
        server = UDPServer(LOCAL_IP, server_port, timeout=timeout)
        client = UDPClient(timeout=timeout).connect_to(LOCAL_IP, server_port, own_ip=LOCAL_IP, own_port=client_port)
        self.sockets.append(server)
        self.sockets.append(client)
        return server, client

    def _tcp_server_and_client(self, port, timeout=None):
        server = TCPServer(LOCAL_IP, port, timeout=timeout)
        client = TCPClient(timeout=timeout).connect_to(LOCAL_IP, port)
        self.sockets.append(server)
        self.sockets.append(client)
        return server, client

    def _server_gets(self, name, text):
        msg = self.net.server_receive(name)
        self.assertEquals(text, msg)


if __name__ == "__main__":
    unittest.main()
