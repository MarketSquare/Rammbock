import unittest
from Protocol import Protocol

class TestProtocol(unittest.TestCase):

    def setUp(self, *args, **kwargs):
        self._protocol = Protocol(test)

    def tearDown(self, *args, **kwargs):
        pass
