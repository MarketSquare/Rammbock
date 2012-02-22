import unittest
from Message import _MessageStruct


class TestMessages(unittest.TestCase):

    def test_in(self):
        msg = _MessageStruct('foo')
        msg['a'] = 1
        msg['b'] = 1
        msg['c'] = 1
        self.assertTrue('a' in msg)
        self.assertFalse('d' in msg)


if __name__ == "__main__":
    unittest.main()