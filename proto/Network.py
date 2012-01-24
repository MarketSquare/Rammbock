import socket

BUFFER_SIZE = 65536

class _WithTimeouts(object):

    _default_timeout = 10

    def _get_timeout(self, timeout):
        if str(timeout).lower() == 'none':
            return self._default_timeout
        elif str(timeout).lower() == 'blocking':
            return None
        return float(timeout)

    def _set_default_timeout(self, timeout):
        self._default_timeout = self._get_timeout(timeout)


class _Server(_WithTimeouts):

    def __init__(self, ip, port, timeout=None):
        self._ip = ip
        self._port = port
        self._timeout = timeout
        self._set_default_timeout(self._timeout)

    def _bind_socket(self):
        self._socket.bind((self._ip, int(self._port)))
        self._is_connected = True

    def close(self):
        if self._is_connected:
            self._is_connected = False
            self._socket.close()


class UDPServer(_Server):

    def __init__(self, ip, port, timeout=None):
        _Server.__init__(self, ip, port, timeout)
        self._init_socket()

    def _init_socket(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._bind_socket()

    def receive_from(self, timeout=None):
        timeout = self._get_timeout(timeout)
        try:
            self._socket.settimeout(timeout)
            return self._socket.recvfrom(BUFFER_SIZE)
        # If we are sending to a machine that wont listen, then reading 
        # becomes impossible from this socket on windows.
        # On linux sending to a port that is not listening causes following
        # send operations to fail.
        except socket.error:
            self._init_socket()
            self._socket.settimeout(timeout)
            return self._socket.recvfrom(BUFFER_SIZE)

    def read(self, timeout=None):
        return self.receive_from(timeout)[0]

    def send_to(self, msg, ip, port):
        self._socket.sendto(msg, (ip,int(port)))


class TCPServer(_Server):

    def __init__(self, ip, port, timeout=None):
        _Server.__init__(self, ip, port, timeout)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._bind_socket()
        self._socket.listen(1)
        self._connections = _NamedCache('connection')

    def read(self, timeout=None):
        return self.receive_from(timeout)[0]

    def receive_from(self, timeout=None, alias=None):
        connection = self._connections.get(alias)[0]
        timeout = self._get_timeout(timeout)
        connection.settimeout(timeout)
        return connection.recvfrom(BUFFER_SIZE)

    def accept_connection(self, alias=None):
        connection, client_address = self._socket.accept()
        self._connections.add((connection, client_address), alias)
        return client_address

    def send(self, msg, alias=None):
        self._connections.get(alias)[0].send(msg)


class _Client(_WithTimeouts):

    def __init__(self, send_callback=None, read_callback=None, timeout=None):
        self._is_connected = False
        self._send_callback = send_callback
        self._read_callback = read_callback
        self._init_socket()
        self._set_default_timeout(timeout)

    def set_own_ip_and_port(self, ip=None, port=None):
        if ip and port:
            self._socket.bind((ip, port))
        elif ip:
            self.socket.bind((ip, 0))
        elif port:
            self.socket.bind(("", port))
        else:
            raise Exception("You must specify host or port")

    def connect_to(self, server_ip, server_port, own_ip=None, own_port=None):
        if not self._is_connected:
            self._server_ip = server_ip
            if own_ip and own_port:
                self._socket.bind((own_ip, int(own_port)))
            self._socket.connect((server_ip, int(server_port)))
            self._is_connected = True
        return self

    def send(self, msg):
        if self._send_callback:
            self._send_callback(msg)
        self._socket.sendall(msg)

    def read(self, timeout=None):
        timeout = self._get_timeout(timeout)
        self._socket.settimeout(timeout)
        msg = self._socket.recv(self._size_limit)
        if self._read_callback:
            self._read_callback(msg)
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
            self._socket.shutdown(socket.SHUT_RDWR)
            self._socket.close()


class UDPClient(_Client):

    _size_limit = BUFFER_SIZE

    def _init_socket(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


class TCPClient(_Client):

    _size_limit = 1000000

    def _init_socket(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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

    def iterator(self):
        return self._cache.itervalues()
