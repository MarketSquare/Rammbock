import socket
import time
from binary_conversions import to_hex

UDP_BUFFER_SIZE = 65536
TCP_BUFFER_SIZE = 1000000

class _WithTimeouts(object):

    _default_timeout = 10

    def _get_timeout(self, timeout):
        if not timeout or str(timeout).lower() == 'none':
            return self._default_timeout
        elif str(timeout).lower() == 'blocking':
            return None
        return float(timeout)

    def _set_default_timeout(self, timeout):
        self._default_timeout = self._get_timeout(timeout)


class _Server(_WithTimeouts):

    def __init__(self, ip, port, timeout=None):
        self._ip = ip
        self._port = int(port)
        self._set_default_timeout(timeout)

    def _bind_socket(self):
        self._socket.bind((self._ip, self._port))
        self._is_connected = True

    def close(self):
        if self._is_connected:
            self._is_connected = False
            self._socket.close()
            self._message_stream = None

    def _get_message_stream(self, connection):
        if not self._protocol:
            return None
        return self._protocol.get_message_stream(BufferedStream(connection, self._default_timeout))


class UDPServer(_Server):

    def __init__(self, ip, port, timeout=None, protocol=None):
        _Server.__init__(self, ip, port, timeout)
        self._protocol = protocol
        self._last_client = None
        self._init_socket()

    def _init_socket(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._bind_socket()
        self._message_stream = self._get_message_stream(self)

    def receive_from(self, timeout=None, alias=None):
        self._check_no_alias(alias)
        timeout = self._get_timeout(timeout)
        self._socket.settimeout(timeout)
        msg, (ip, host) = self._socket.recvfrom(UDP_BUFFER_SIZE)
        print "*DEBUG* Read %s" % to_hex(msg)
        self._last_client = (ip, host)
        return msg, ip, host

    def _check_no_alias(self, alias):
        if alias:
            raise Exception('Connection aliases are not supported on UDP Servers')

    def receive(self, timeout=None, alias=None):
        return self.receive_from(timeout, alias)[0]

    def send_to(self, msg, ip, port):
        print "*DEBUG* Send %s" % to_hex(msg)
        self._socket.sendto(msg, (ip,int(port)))

    def send(self, msg, alias=None):
        if alias:
            raise Exception('UDP Server does not have connection aliases. Tried to use connection %s.' % alias)
        if not self._last_client:
            raise Exception('Server can not send to default client, because it has not received messages from clients.')
        self.send_to(msg, *self._last_client)

    def get_message(self, message_template, timeout=None):
        return self._message_stream.get(message_template, timeout=timeout)


class TCPServer(_Server):

    def __init__(self, ip, port, timeout=None, protocol=None):
        _Server.__init__(self, ip, port, timeout)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._bind_socket()
        self._socket.listen(1)
        self._connections = _NamedCache('connection')
        self._protocol = protocol

    def receive(self, timeout=None, alias=None):
        return self.receive_from(timeout, alias)[0]

    def receive_from(self, timeout=None, alias=None):
        connection, (ip, host) = self._connections.get(alias)
        timeout = self._get_timeout(timeout)
        connection.settimeout(timeout)
        msg = connection.recv(TCP_BUFFER_SIZE)
        print "*DEBUG* Read %s" % to_hex(msg)
        return msg, ip, host

    def accept_connection(self, alias=None):
        connection, client_address = self._socket.accept()
        self._connections.add((connection, client_address), alias)
        return client_address

    def send(self, msg, alias=None):
        print "*DEBUG* Send %s" % to_hex(msg)
        self._connections.get(alias)[0].send(msg)

    def send_to(self, *args):
        raise Exception("TCP server cannot send to a specific address.")

    def close(self):
        if self._is_connected:
            self._is_connected = False
            for connection, _ in self._connections:
                connection.close()
            self._socket.close()

    def get_message(self, message_template, timeout=None, alias=None):
        # Wrap connection to server like wrapper with message logging
        raise Exception("Not yet implemented")

    # TODO: Close single connection


class _Client(_WithTimeouts):

    def __init__(self, timeout=None, protocol=None):
        self._is_connected = False
        self._init_socket()
        self._set_default_timeout(timeout)
        self._protocol = protocol
        self._message_stream = None

    def _get_message_stream(self):
        if not self._protocol:
            return None
        return self._protocol.get_message_stream(BufferedStream(self, self._default_timeout))

    def set_own_ip_and_port(self, ip=None, port=None):
        if ip and port:
            self._socket.bind((ip, int(port)))
        elif ip:
            self._socket.bind((ip, 0))
        elif port:
            self._socket.bind(("", int(port)))
        else:
            raise Exception("You must specify host or port")

    def connect_to(self, server_ip, server_port):
        if self._is_connected:
            raise Exception('Client already connected!')
        self._server_ip = server_ip
        self._socket.connect((server_ip, int(server_port)))
        self._message_stream = self._get_message_stream()
        self._is_connected = True
        return self

    def send(self, msg):
        print "*DEBUG* Send %s" % to_hex(msg)
        self._socket.sendall(msg)

    def receive(self, timeout=None):
        timeout = self._get_timeout(timeout)
        self._socket.settimeout(timeout)
        msg = self._socket.recv(self._size_limit)
        print "*DEBUG* Read %s" % to_hex(msg)
        return msg

    def empty(self):
        result = True
        try:
            while (result):
                result = self.read(timeout=0.0)
        except (socket.timeout, socket.error):
            pass
        if self._message_stream:
            self._message_stream.empty()

    def close(self):
        if self._is_connected:
            self._is_connected = False
            self._socket.close()
            self._message_stream = None

    def get_address(self):
        return self._socket.getsockname()

    def get_message(self, message_template, timeout=None):
        return self._message_stream.get(message_template, timeout=timeout)


class UDPClient(_Client):

    _size_limit = UDP_BUFFER_SIZE

    def _init_socket(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


class TCPClient(_Client):

    _size_limit = TCP_BUFFER_SIZE

    def _init_socket(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


class _NamedCache(object):

    def __init__(self, basename):
        self._basename=basename
        self._counter=0
        self._cache = {}
        self._current = None

    def add(self, value, name=None):
        if not name:
            name=self._next_name()
        self._cache[name] = value
        self._current = value

    def _next_name(self):
        self._counter+=1
        return self._basename+str(self._counter)

    def get(self, name=None):
        if not name:
            return self._current
        return self._cache[name]

    def __iter__(self):
        return self._cache.itervalues()


class BufferedStream(_WithTimeouts):

    def __init__(self, connection, default_timeout):
        self._connection = connection
        self._buffer = ''
        self._default_timeout = default_timeout

    def read(self, size, timeout=None):
        result = ''
        timeout = float(timeout if timeout else self._default_timeout)
        cutoff = time.time() + timeout
        while time.time() < cutoff:
            result += self._get(size-len(result))
            if len(result) == size:
                return result
            self._fill_buffer(timeout)
        raise AssertionError('Timeout %ds exceeded.' % timeout)

    def _get(self, size):
        if not self._buffer:
            return ''
        result = self._buffer[:size]
        self._buffer = self._buffer[size:]
        return result

    def _fill_buffer(self, timeout):
        self._buffer += self._connection.receive(timeout=timeout)

    def empty(self):
        self.buffer = ''