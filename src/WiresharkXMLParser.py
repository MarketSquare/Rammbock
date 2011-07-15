from xml.dom import minidom
from sys import argv
from time import asctime
import re


LENGTH_FROM_OBJ = re.compile(r'<field.*size="(\w*)"')
SHOW_FROM_OBJ = re.compile(r'<field.*show="(.*?)"')
VALUE_FROM_OBJ = re.compile(r'<field.*value="(.*?)"')
NAME_FROM_OBJ = re.compile(r'<field.*name="(.*?)"')
POS_FROM_OBJ = re.compile(r'<field.*pos="(.*?)"')

class Parser(object):
    def __init__(self, infile, outfile, tcname):
        self.prevnode = None
        self.temp_binary = ""
        self.temp_name = ""
        self.of = []
        self.infile = infile
        self.outfile = outfile
        self.tcname = tcname
        self.xmldoc = None

    def make_file(self):
        self._append_meta_information()
        self.xmldoc = minidom.parse(self.infile)
        self._add_test_case()
        self._add_keywords()
        self._write_file()

    def _add_keywords(self):
        self.of.append("*** Keywords ***\n")
        for node in self.xmldoc.childNodes:
            self.of.append(self._show(node) + "\n")
            self._handle_node(node)
            self.of.append("\n")

    def _write_file(self):
        output_file = open(self.outfile, 'w')
        for line in self.of:
            output_file.write(line)
        output_file.close()

    def _add_test_case(self):
        self.of.append("*** Test Cases ***\n")
        self.of.append(self.tcname + '\n')
        self.of.append("    Create Message\n")
        for node in  self.xmldoc.childNodes:
            self.of.append("    " + self._show(node) + "\n")
        self.of.append("    Client Sends Data\n")
        self.of.append("\n")

    def _append_meta_information(self):
        self.of.append("*** Settings ***\n")
        self.of.append("Documentation    This test file has been generated automatically with PDML to Robot framework test case converter (WiresharkXMLParser.py) at " + asctime() + ".\n")
        self.of.append("Test Setup      UDP Server and Client are initialized\n")
        self.of.append("Test Teardown   Close Connections\n")
        self.of.append("Default Tags    regression\n")
        self.of.append("Library         rammbock.Rammbock\n")
        self.of.append("Resource        ../resources/Messaging.txt\n")
        self.of.append("Resource        ../protocols/gtp/v2.txt\n")
        self.of.append("\n")

    def _handle_node(self, node) :
        if not node.toxml().startswith('\n'):
            length = self._length(node)
            if length is 1 or len(node.childNodes) is 0:
                if self._pos(node) == self._pos(self.prevnode) and self._name(self.prevnode) != "":
                    self.of = self.of[:-1]
                    if self.temp_name == "":
                        self.temp_name = self._name(self.prevnode) + ', ' + self._name(node)
                        self.temp_binary = self._value(self.prevnode)+self._value(node)
                    else:
                        self.temp_name = self.temp_name + ', ' + self._name(node)
                        self.temp_binary = self.temp_binary+self._value(node)
                else:
                    if len(self.temp_binary) > 0:
                        try:
                            self.of.append("    Add Decimal As Binary    " + str(int(self.temp_binary, 2)) + "    " + str(self._length(self.prevnode)) + "    #" + self.temp_name + "\n")
                        except ValueError:
                            self.of.append("    Add Decimal As Binary    " + str(int(self.temp_binary, 16)) + "    " + str(self._length(self.prevnode)) + "    #" + self.temp_name + "\n")
                        self.temp_name = ""
                        self.temp_binary = ""
                    if self._name(node) == "":
                        to_add = "    Add Decimal As Binary    " + self._value(node) + "    " + str(self._length(node)) + "    #" + self._show(node) + "\n"
                    else:
                        to_add = "    Add Decimal As Binary    " + self._show(node) + "    " + str(self._length(node)) + "    #" + self._name(node) + "\n"
                    self.of.append(to_add)
            elif len(node.childNodes) > 0:
                for subnode in node.childNodes:
                    self._handle_node(subnode)
            self.prevnode = node

    def _length(self, node):
        return int(LENGTH_FROM_OBJ.match(node.toxml()).group(1))

    def _show(self, node):
        return SHOW_FROM_OBJ.match(node.toxml()).group(1)

    def _value(self, node):
        return VALUE_FROM_OBJ.match(node.toxml()).group(1)

    def _name(self, node):
        if node is None:
            return ""
        else:
            return NAME_FROM_OBJ.match(node.toxml()).group(1)

    def _pos(self, node):
        if node is None:
            return "-1"
        else:
            return POS_FROM_OBJ.match(node.toxml()).group(1)

if __name__ == "__main__":
    if len(argv) is 4:
        Parser(argv[1], argv[2], argv[3]).make_file()
    else:
        print "Usage: python wiresharkXMLParser.py infile.xml outfile.txt test\\ case\\ name"
