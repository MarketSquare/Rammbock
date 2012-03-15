import unittest
import time
import socket
from threading import Timer
from Networking import UDPServer, TCPServer, UDPClient, TCPClient, BufferedStream
from templates.containers import Protocol
from templates.primitives import UInt, PDU

LOCAL_IP = '127.0.0.1'
CONNECTION_ALIAS = "Connection alias"

ports = {'SERVER_PORT': 12345,
         'CLIENT_PORT': 54321}

class TestNetworking(unittest.TestCase):

    def setUp(self):
        self.sockets = []
        for key in ports:
            ports[key] = ports[key] + 1

    def tearDown(self, *args, **kwargs):
        for sock in self.sockets:
            sock.close()
        return unittest.TestCase.tearDown(self, *args, **kwargs)

    def test_send_and_receive_udp(self):
        server, client = self._udp_server_and_client(ports['SERVER_PORT'], ports['CLIENT_PORT'])
        client.send('foofaa')
        self._assert_receive(server, 'foofaa')

    def test_server_send_udp(self):
        server, client = self._udp_server_and_client(ports['SERVER_PORT'], ports['CLIENT_PORT'])
        server.send_to('foofaa', LOCAL_IP, ports['CLIENT_PORT'])
        self._assert_receive(client, 'foofaa')

    def test_server_send_tcp(self):
        server, client = self._tcp_server_and_client(ports['SERVER_PORT'], ports['CLIENT_PORT'])
        server.accept_connection()
        server.send('foofaa')
        self._assert_receive(client, 'foofaa')

    def test_send_and_receive_tcp(self):
        server, client = self._tcp_server_and_client(ports['SERVER_PORT'], ports['CLIENT_PORT'])
        client.send('foofaa')
        server.accept_connection()
        self._assert_receive(server, 'foofaa')

    def test_tcp_server_with_queued_connections(self):
        server, client = self._tcp_server_and_client(ports['SERVER_PORT'], ports['CLIENT_PORT'])
        TCPClient().connect_to(LOCAL_IP, ports['SERVER_PORT'])
        server.accept_connection()
        server.accept_connection()

    def test_tcp_server_with_named_connection(self):
        server = TCPServer(LOCAL_IP, 1337)
        client = TCPClient().connect_to(LOCAL_IP, 1337)
        server.accept_connection(alias=CONNECTION_ALIAS + "1")
        self.assertTrue(server._connections.get(CONNECTION_ALIAS + "1"))

    def test_setting_port_no_ip(self):
        server, client = self._udp_server_and_client(ports['SERVER_PORT'], ports['CLIENT_PORT'], client_ip='')
        server.send_to('foofaa', LOCAL_IP, client.get_address()[1])
        self._assert_receive(client, 'foofaa')

    def test_setting_ip_no_port(self):
        server, client = self._udp_server_and_client(ports['SERVER_PORT'], '')
        server.send_to('foofaa', *client.get_address())
        self._assert_receive(client, 'foofaa')

    def test_setting_client_default_timeout(self):
        _, client = self._udp_server_and_client(ports['SERVER_PORT'], ports['CLIENT_PORT'], timeout=0.1)
        self._assert_timeout(client)

    def test_setting_timeout_to_0(self):
        server, client = self._udp_server_and_client(ports['SERVER_PORT'], ports['CLIENT_PORT'], timeout=3)
        self._assert_timeout_error(server, 0.0)
        self._assert_timeout_error(client, '0.0')

    def test_overriding_client_read_timeout(self):
        _, client = self._udp_server_and_client(ports['SERVER_PORT'], ports['CLIENT_PORT'], timeout=3)
        self._assert_timeout(client, 0.1)

    def test_overriding_server_read_timeout(self):
        server, _ = self._udp_server_and_client(ports['SERVER_PORT'], ports['CLIENT_PORT'], timeout=3)
        self._assert_timeout(server, 0.1)

    def test_setting_server_default_timeout(self):
        server, _ = self._udp_server_and_client(ports['SERVER_PORT'], ports['CLIENT_PORT'], timeout=0.1)
        self._assert_timeout(server)

    def test_blocking_timeout(self):
        server, client = self._udp_server_and_client(ports['SERVER_PORT'], ports['CLIENT_PORT'], timeout=0.1)
        t = Timer(0.2, client.send, args=['foofaa'])
        t.start()
        self.assertEquals(server.receive(timeout='blocking'), 'foofaa')

    def test_empty_udp_stream(self):
        server, client = self._udp_server_and_client(ports['SERVER_PORT'], ports['CLIENT_PORT'], timeout=0.1)
        self._verify_emptying(server, client)

    def test_empty_tcp_stream(self):
        server, client = self._tcp_server_and_client(ports['SERVER_PORT'], timeout=0.1)
        server.accept_connection()
        self._verify_emptying(server, client)

    def _verify_emptying(self, server, client):
        client.send('to connect')
        server.receive()
        client.send('before emptying')
        server.send('before emptying')
        client.empty()
        server.empty()
        client.send('after')
        server.send('after')
        self._assert_receive(client, 'after')
        self._assert_receive(server, 'after')

    def _assert_timeout(self, node, timeout=None):
        self._assert_timeout_with_type(node, socket.timeout, timeout)

    def _assert_timeout_error(self, node, timeout=None):
        self._assert_timeout_with_type(node, socket.error, timeout)

    def _assert_timeout_with_type(self, node, exception_type, timeout):
        start_time = time.time()
        self.assertRaises(exception_type, node.receive, timeout)
        self.assertTrue(time.time() - 0.5 < start_time)

    def _assert_receive(self, receiver, msg):
        self.assertEquals(receiver.receive(), msg)

    def _udp_server_and_client(self, server_port, client_port, client_ip=LOCAL_IP, timeout=None):
        server = UDPServer(LOCAL_IP, server_port, timeout=timeout)
        client = UDPClient(timeout=timeout)
        client.set_own_ip_and_port(client_ip, client_port)
        client.connect_to(LOCAL_IP, server_port)
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


def _get_template():
    protocol = Protocol('Test')
    protocol.add(UInt(1, 'id', 1))
    protocol.add(UInt(2, 'length', None))
    protocol.add(PDU('length-2'))
    return protocol


class TestBufferedStream(unittest.TestCase):

    DATA = 'foobardiibadaa'
    
    def setUp(self):
        self._buffered_stream = BufferedStream(MockConnection(self.DATA), 0.1)
    
    def test_normal_read(self):
        self.assertEquals(self.DATA, self._buffered_stream.read(len(self.DATA)))

    def test_empty(self):
        self._buffered_stream.read(len('foobar'))
        self._buffered_stream.empty()
        self.assertRaises(AssertionError, self._buffered_stream.read, len(self.DATA)-len('foobar'))


class MockConnection(object):
    
    def __init__(self, mock_data_to_receive):
        self._data = mock_data_to_receive
    
    def receive(self, timeout):
        ret = self._data
        self._data = ''
        return ret


if __name__ == "__main__":
    unittest.main()
