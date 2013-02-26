from unittest import TestCase
from Rammbock.templates.containers import BinaryContainerTemplate
from Rammbock.templates.primitives import UInt, Binary
from Rammbock.binary_tools import to_bin


class TestBinaryContainerTemplate(TestCase):

    def test_verify_field_length_fails(self):
        container = BinaryContainerTemplate('foo', None)
        container.add(Binary(3, 'threeBits', None))
        self.assertRaises(AssertionError, container.verify)

    def test_verify_single_byte_field_length_passes(self):
        container = BinaryContainerTemplate('foo', None)
        container.add(Binary(4, 'firstFour', None))
        container.add(Binary(4, 'lastFour', None))
        container.verify()

    def test_verify_multi_byte_field_length_passes(self):
        container = BinaryContainerTemplate('foo', None)
        for length, name in zip([4, 4, 5, 3, 1, 3, 12], ['a', 'b', 'c', 'd', 'e', 'f', 'g']):
            container.add(Binary(length, name, None))
        container.verify()

    def test_verify_only_binary_field_passes(self):
        container = BinaryContainerTemplate('foo', None)
        container.add(Binary(1, 'oneBit', None))
        self.assertRaises(AssertionError, container.add, UInt(2, 'intsNotAllowed', None))

    def test_decode_container(self):
        container = self._2_byte_container()
        decoded = container.decode(to_bin("0x9001"))
        self.assertEqual(1, decoded.oneBit.int)
        self.assertEqual(1, decoded.threeBits.int)
        self.assertEqual(1, decoded.twelveBits.int)

    def test_decode_little_endian_container(self):
        container = self._2_byte_container()
        decoded = container.decode(to_bin("0x0190"), little_endian=True)
        self.assertEqual(1, decoded.oneBit.int)
        self.assertEqual(1, decoded.threeBits.int)
        self.assertEqual(1, decoded.twelveBits.int)
        self.assertEquals(decoded._raw, to_bin("0x0190"))

    def test_encode_little_endian_container(self):
        container = self._2_byte_container()
        encoded = container.encode({'foo.threeBits': 1, 'foo.twelveBits': 1}, little_endian=True)
        self.assertEqual(1, encoded.oneBit.int)
        self.assertEqual(1, encoded.threeBits.int)
        self.assertEqual(1, encoded.twelveBits.int)
        self.assertEquals(encoded._raw, to_bin("0x0190"))

    def test_decode_longer_data_than_field(self):
        container = self._1_byte_container()
        decoded = container.decode(to_bin("0b0000 0001 1111 1111"))
        self.assertEqual(0, decoded.spare.int)
        self.assertEqual(1, decoded.value.int)

    def _1_byte_container(self):
        container = BinaryContainerTemplate('foo', None)
        container.add(Binary(4, 'spare', 0))
        container.add(Binary(4, 'value', 1))
        return container

    def _2_byte_container(self):
        container = BinaryContainerTemplate('foo', None)
        container.add(Binary(1, 'oneBit', 1))
        container.add(Binary(3, 'threeBits', 7))
        container.add(Binary(12, 'twelveBits', 4095))
        return container
