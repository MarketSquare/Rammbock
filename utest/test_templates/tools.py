import socket


class _MockStream(object):

    def __init__(self, data):
        self.data = data

    def read(self, length, timeout=None):
        if length > len(self.data):
            if timeout:
                raise socket.timeout('timeout')
            else:
                raise AssertionError('No timeout, but out of data.')
        result = self.data[:length]
        self.data = self.data[length:]
        return result

    def return_data(self, data):
        self.data = data + self.data

    def empty(self):
        self.data = ''
