import unittest
from Interface import get_ip_address

class Test(unittest.TestCase):


    def testName(self):
        self.assertEqual(get_ip_address('lo'), '127.0.0.1')

    def testNameNotFound(self):
        self.assertEqual(get_ip_address('doesnotexist'), '')
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()