import unittest
from Interface import get_ip_address

class Test(unittest.TestCase):


    def testName(self):
        POSSIBLE_IFACES = ['lo', 'lo0', 
                'Ethernet adapter Local Area Connection']
        ip_addresses = [get_ip_address(iface) for iface in POSSIBLE_IFACES]
        self.assertTrue('127.0.0.1' in ip_addresses)

    def testNameNotFound(self):
        self.assertEqual(get_ip_address('doesnotexist'), '')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
