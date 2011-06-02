import unittest
from rammbock import Rammbock
from rammbock.Encode import encode_to_bin
from robot.utils.asserts import assert_equal

TEST_APPLICATION_PROTOCOL = 'testApplicationProtocol'

class Test(unittest.TestCase):

    def setUp(self):
        self.rammbock = Rammbock()
        self.message = self._create_example_message()
        self.rammbock.use_application_protocol(TEST_APPLICATION_PROTOCOL)

    def test_create_message(self):
        self.rammbock.create_message('test')
        actual = self.rammbock.message
        expected = self.message
        assert_equal (expected.header[0].name, actual.header[0].name)
        assert_equal (expected.ie[0].name, actual.ie[0].name)

    def test_encode_object_to_bin(self):
        print self.message
        bin_message = encode_to_bin(self.message)
        #TODO: check the size of actual content
        assert_equal(bin_message, 'protocol testApplicationProtocol message Hello world! ')

    def _create_example_message(self):
        class Object:
            pass

        class Message(object):
            header = [None]
            header[0] = Object()
            header[0].length = u'22'
            header[0].name = u'protocol'
            header[0].data = u'testApplicationProtocol'
            ie = [None]
            ie[0] = Object()
            ie[0].length= u'11'
            ie[0].name= u'message'
            ie[0].data= u'Hello world!'
#            ie[1] = Object()
#            ie[1].ie = [None]
#            ie[1].ie[0] = Object()
#            ie[1].ie[0].length = u'4'
#            ie[1].ie[0].name= u'test'
#            ie[1].ie[0].data= u'test'
        return Message()



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
