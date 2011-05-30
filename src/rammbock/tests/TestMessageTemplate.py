import unittest
from rammbock import Rammbock
from rammbock.Message import Message
from rammbock import Encode


TEST_APPLICATION_PROTOCOL = 'testApplicationProtocol'

class Test(unittest.TestCase):


    def setUp(self):
        self._create_example_message()
        self.rammbock = Rammbock()
        self.rammbock.use_application_protocol(TEST_APPLICATION_PROTOCOL)

    def testCreateMessage(self):
        self.rammbock.create_message('testMessage')
        actual = self.rammbock.message
        expected = self.message
        assert(expected.getHeader('protocol'), actual.getheader('protocol'))
        assert(expected.getIe('message'), actual.getIe('message'))

    def testEncodeObjectToBin(self):
        bin_message = Encode.encode_to_bin(self.message)
        #TODO: check the size of actual content
        assert(bin_message, 1234)


    def _create_example_message(self):
        self.message = Message()
        self.message.addHeader('protocol', TEST_APPLICATION_PROTOCOL, 22)
        self.message.addIe('message', 'Hello world!', 11)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
