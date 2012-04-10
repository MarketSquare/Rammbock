import os
from Rammbock import Rammbock
from robot.libraries.BuiltIn import BuiltIn
from message_sequence import SeqdiagGenerator


class RammbockLibrary(Rammbock):

    def u8(self, name, value=None, align=None):
        """Add an unsigned 1 byte integer field to template.

        This is an convenience method that simply calls `Uint` keyword with predefined length."""
        self.uint(1, name, value, align)

    def u16(self, name, value=None, align=None):
        """Add an unsigned 2 byte integer field to template.

        This is an convenience method that simply calls `Uint` keyword with predefined length."""
        self.uint(2, name, value, align)

    def u24(self, name, value=None, align=None):
        """Add an unsigned 3 byte integer field to template.

        This is an convenience method that simply calls `Uint` keyword with predefined length."""
        self.uint(3, name, value, align)

    def u32(self, name, value=None, align=None):
        """Add an unsigned 4 byte integer field to template.

        This is an convenience method that simply calls `Uint` keyword with predefined length."""
        self.uint(4, name, value, align)

    def u64(self, name, value=None, align=None):
        """Add an unsigned 8 byte integer field to template.

        This is an convenience method that simply calls `Uint` keyword with predefined length."""
        self.uint(8, name, value, align)

    def u128(self, name, value=None, align=None):
        """Add an unsigned 16 byte integer field to template.

        This is an convenience method that simply calls `Uint` keyword with predefined length."""
        self.uint(16, name, value, align)

    def array(self, size, type, name, *params):
        """Define a new array of given `size` and containing fields of type `type`.

        `name` if the name of this array element. The `type` is the name of keyword that is executed as the contents of
        the array and optional extra parameters are passed as arguments to this keyword. This is a convenience method for
        calling `New List` and `End List` with `type` between them.
        """
        self.new_list(size, name)
        BuiltIn().run_keyword(type, '', *params)
        self.end_list()

    def container(self, name, length, type, *params):
        """Define a container with given length.

        This is a convenience method creating a `Struct` with `length` containing fields defined in `type`.
        """
        self.struct('Container', name, 'length=%s' % length)
        BuiltIn().run_keyword(type, *params)
        self.end_struct()

    def embed_seqdiag_sequence(self):
        """Create a message sequence diagram png file to output folder and embed the image to log file.

        You need to have seqdiag installed to create the sequence diagram. See http://blockdiag.com/en/seqdiag/
        """
        test_name = BuiltIn().replace_variables('${TEST NAME}')
        outputdir = BuiltIn().replace_variables('${OUTPUTDIR}')
        path = os.path.join(outputdir, test_name+'.seqdiag')
        SeqdiagGenerator().compile(path, self._message_sequence)