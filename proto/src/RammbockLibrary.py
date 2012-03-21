from Rammbock import Rammbock
from robot.libraries.BuiltIn import BuiltIn


class RammbockLibrary(Rammbock):

    def u8(self, name, value=None, align=None):
        self.uint(1, name, value, align)

    def u16(self, name, value=None, align=None):
        self.uint(2, name, value, align)

    def u32(self, name, value=None, align=None):
        self.uint(4, name, value, align)

    def u64(self, name, value=None, align=None):
        self.uint(8, name, value, align)

    def u128(self, name, value=None, align=None):
        self.uint(16, name, value, align)

    def array(self, size, type, name, *params):
        self.new_list(size, name)
        BuiltIn().run_keyword(type, '', *params)
        self.end_list()

    def container(self, name, length, type, *params):
        self.struct('Container', name, 'length=%s'% length)
        BuiltIn().run_keyword(type, *params)
        self.end_struct()
