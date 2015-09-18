#  Copyright 2014 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os

from robot.libraries.BuiltIn import BuiltIn
from .core import RammbockCore
from .message_sequence import SeqdiagGenerator
from .version import VERSION


class Rammbock(RammbockCore):
    """Rammbock is a binary protocol testing library for Robot Test Automation Framework.

    To use Rammbock you need to first define a protocol, start the clients and servers you are going to mock,
    and then define a message template for each message you are going to send or receive.

    Example:

    | *Settings * |
    | Library     | Rammbock |

    | *Test Cases*  |
    |  Send message |  Define simple protocol  |
    |               |  Start server     |
    |               |  Start client     |
    |               |  Send message     | status:0xcafebabe |
    |               |  Verify server gets status |  0xcafebabe |
    |               |  [Teardown]       |   `Reset Rammbock` |

    | *Keywords*      |
    | Define simple protocol  |  `New protocol`   | SimpleProtocol |
    |                 |  `u8`                     | msgId             |
    |                 |  `u8`                     | messageLength     |
    |                 |  `pdu`                    | messageLength - 2 |
    |                 |  `End protocol`           |
    |  |
    | Start server    |  `Start UDP server` | 127.0.0.1 |  8282 | protocol=SimpleProtocol |
    |  |
    | Start client    |  `Start UDP client` | protocol=SimpleProtocol |
    |                 |  `Connect`          | 127.0.0.1 |  8282 |
    |     |   |    |  |  |
    | Send message    | [Arguments] | @{params} |
    |                 | `New message` | SimpleRequest | SimpleProtocol |  msgId:0xff |
    |                 |  `u32`         | status        |
    |                 |  `Client sends message` | @{params} |
    |  |
    | Verify server gets status | [Arguments] | ${status} |
    |                 | ${msg} = | `Server receives message` |
    |                 | Should be equal | ${msg.status.hex} | ${status} |


    """

    ROBOT_LIBRARY_VERSION = VERSION

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

    def u40(self, name, value=None, align=None):
        """Add an unsigned 5 byte integer field to template.

        This is an convenience method that simply calls `Uint` keyword with predefined length."""
        self.uint(5, name, value, align)

    def u64(self, name, value=None, align=None):
        """Add an unsigned 8 byte integer field to template.

        This is an convenience method that simply calls `Uint` keyword with predefined length."""
        self.uint(8, name, value, align)

    def u128(self, name, value=None, align=None):
        """Add an unsigned 16 byte integer field to template.

        This is an convenience method that simply calls `Uint` keyword with predefined length."""
        self.uint(16, name, value, align)

    def i8(self, name, value=None, align=None):
        """Add an 1 byte integer field to template.

        This is an convenience method that simply calls `Int` keyword with predefined length."""
        self.int(1, name, value, align)

    def i32(self, name, value=None, align=None):
        """Add an 32 byte integer field to template.

        This is an convenience method that simply calls `Int` keyword with predefined length."""
        self.int(4, name, value, align)

    def array(self, size, type, name, *parameters):
        """Define a new array of given `size` and containing fields of type `type`.

        `name` if the name of this array element. The `type` is the name of keyword that is executed as the contents of
        the array and optional extra parameters are passed as arguments to this keyword.

        Examples:
        | Array | 8 | u16 | myArray |

        | u32 | length |
        | Array | length | someStruct | myArray | <argument for someStruct> |
        """
        self._new_list(size, name)
        BuiltIn().run_keyword(type, '', *parameters)
        self._end_list()

    def container(self, name, length, type, *parameters):
        """Define a container with given length.

        This is a convenience method creating a `Struct` with `length` containing fields defined in `type`.
        """
        self.new_struct('Container', name, 'length=%s' % length)
        BuiltIn().run_keyword(type, *parameters)
        self.end_struct()

    def case(self, size, kw, *parameters):
        """An element inside a bag started with `Start Bag`.

        The first argument is size which can be absolute value like `1`, a range
        like `0-3`, or just `*` to accept any number of elements.

        Examples:
        | Start bag | intBag |
        | case | 0-1 | u8 | foo | 42 |
        | case | 0-2 | u8 | bar | 1 |
        | End bag |
        """
        # TODO: check we are inside a bag!
        self._start_bag_case(size)
        BuiltIn().run_keyword(kw, *parameters)
        self._end_bag_case()

    def embed_seqdiag_sequence(self):
        """Create a message sequence diagram png file to output folder and embed the image to log file.

        You need to have seqdiag installed to create the sequence diagram. See http://blockdiag.com/en/seqdiag/
        """
        test_name = BuiltIn().replace_variables('${TEST NAME}')
        outputdir = BuiltIn().replace_variables('${OUTPUTDIR}')
        path = os.path.join(outputdir, test_name + '.seqdiag')
        SeqdiagGenerator().compile(path, self._message_sequence)
