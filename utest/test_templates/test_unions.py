from unittest import TestCase
from Rammbock.templates.containers import StructTemplate, UnionTemplate
from Rammbock.templates.primitives import UInt, Char
from Rammbock.binary_tools import to_bin
from .tools import *


class TestUnions(TestCase, WithValidation):

    def _check_length(self, length, *fields):
        union = UnionTemplate('Foo', 'foo', parent=None)
        for value in fields:
            union.add(value)
        self.assertEquals(union.get_static_length(), length)

    def test_union_primitive_length(self):
        self._check_length(2, UInt(1, 'a', 1), UInt(2, 'b', 1))
        self._check_length(1, UInt(1, 'a', 1), UInt(1, 'b', 1))
        self._check_length(4, UInt(4, 'a', 4), UInt(1, 'b', 1), UInt(2, 'c', 1))
        self._check_length(16, UInt(1, 'a', 1), Char(16, 'b', 1))
        self._check_length(10, Char(10, 'a', None), Char(10, 'b', None))

    def test_container_union_length(self):
        self._check_length(4, get_pair(), UInt(2, 'b', 1))
        self._check_length(4, UInt(1, 'a', 1), get_recursive_struct())
        self._check_length(6, get_pair(), get_list_of_three())

    def test_fail_on_dynamic_length(self):
        union = UnionTemplate('NotLegal', 'dymagic', parent=None)
        union.add(UInt(2, 'bar', None))
        struct = StructTemplate('Foo', 'foo', parent=None)
        struct.add(UInt(1, 'len', 22))
        struct.add(Char('len', 'dymagic', 'foo'))
        self.assertRaises(Exception, union.add, struct)

    def test_decode_union(self):
        union = self._get_foo_union()
        decoded = union.decode(to_bin('0xcafebabe'))
        self.assertEquals(decoded.small.hex, '0xca')
        self.assertEquals(decoded.medium.hex, '0xcafe')
        self.assertEquals(decoded.large.hex, '0xcafebabe')

    def test_union_length(self):
        union = self._get_foo_union()
        decoded = union.decode(to_bin('0xcafebabe'))
        self.assertEquals(4, len(decoded))

    def test_get_bytes_from_decoded_union(self):
        union = self._get_foo_union()
        decoded = union.decode(to_bin('0xcafebabe'))
        self.assertEquals(decoded._raw, to_bin('0xcafebabe'))

    def _get_foo_union(self):
        union = UnionTemplate('Foo', 'foo', parent=None)
        union.add(UInt(1, 'small', '0xff'))
        union.add(UInt(2, 'medium', '0xf00d'))
        union.add(UInt(4, 'large', None))
        return union

    def test_encode_union(self):
        union = self._get_foo_union()
        encoded = union.encode({'foo': 'medium'}, {})
        self.assertEquals(encoded._raw, to_bin('0xf00d 0000'))

    def test_encode_union_with_param(self):
        union = self._get_foo_union()
        encoded = union.encode({'foo': 'small', 'foo.small': '0xff'}, {})
        self.assertEquals(encoded._raw, to_bin('0xff00 0000'))

    def test_encode_union_without_chosen_union_fails(self):
        union = self._get_foo_union()
        self.assertRaises(AssertionError, union.encode, {'foo.small': '0xff', 'foo.medium': '0xaaaa'}, {})

    def test_validate_union(self):
        union = self._get_foo_union()
        decoded = union.decode(to_bin('0xcafebabe'))
        self._should_pass(union.validate({'foo': decoded}, {'foo.small': '', 'foo.medium': ''}))
        self._should_fail(union.validate({'foo': decoded}, {'foo.small': '0xff', 'foo.medium': ''}), 1)

    def test_validate_struct_union(self):
        struct = get_pair()
        union = self._get_foo_union()
        struct.add(union)
        decoded = struct.decode(to_bin('0xcafebabe f00dd00d'))
        self._should_fail(struct.validate({'pair': decoded}, {}), 3)
