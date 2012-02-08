import socket

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


class UDPServer(_Server):

    def __init__(self, ip, port, timeout=None, protocol=None):
        _Server.__init__(self, ip, port, timeout)
        self._init_socket()
        self._protocol= protocol

    def _init_socket(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._bind_socket()

    def receive_from(self, timeout=None, alias=None):
        self._check_no_alias(alias)
        timeout = self._get_timeout(timeout)
        self._socket.settimeout(timeout)
        msg, (ip, host) = self._socket.recvfrom(UDP_BUFFER_SIZE)
        return msg, ip, host

    def _check_no_alias(self, alias):
        if alias:
            raise Exception('Connection aliases are not supported on UDP Servers')

    def receive(self, timeout=None, alias=None):
        return self.receive_from(timeout, alias)[0]

    def send_to(self, msg, ip, port):
        self._socket.sendto(msg, (ip,int(port)))


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
        return msg, ip, host

    def accept_connection(self, alias=None):
        connection, client_address = self._socket.accept()
        self._connections.add((connection, client_address), alias)
        return client_address

    def send(self, msg, alias=None):
        self._connections.get(alias)[0].send(msg)

    def close(self):
        if self._is_connected:
            self._is_connected = False
            for connection, _ in self._connections:
                connection.close()
            self._socket.close()

    # TODO: Close single connection


class _Client(_WithTimeouts):

    def __init__(self, timeout=None, protocol=None):
        self._protocol = protocol
        self._is_connected = False
        self._init_socket()
        self._set_default_timeout(timeout)

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
        if not self._is_connected:
            self._server_ip = server_ip
            self._socket.connect((server_ip, int(server_port)))
            self._is_connected = True
        return self

    def send(self, msg):
        self._socket.sendall(msg)

    def receive(self, timeout=None):
        timeout = self._get_timeout(timeout)
        self._socket.settimeout(timeout)
        msg = self._socket.recv(self._size_limit)
        return msg

    def empty(self):
        result = True
        try:
            while (result):
                result = self.read(timeout=0.0)
        except (socket.timeout, socket.error):
            pass

    def close(self):
        if self._is_connected:
            self._is_connected = False
            self._socket.close()

    def get_address(self):
        return self._socket.getsockname()

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
