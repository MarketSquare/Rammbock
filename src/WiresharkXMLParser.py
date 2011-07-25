from __future__ import with_statement
from xml.dom import minidom
from sys import argv
from time import asctime
import re


LENGTH_FROM_OBJ = re.compile(r'<field.*size="(\w*)"')
SHOW_FROM_OBJ = re.compile(r'<field.*show="(.*?)"')
VALUE_FROM_OBJ = re.compile(r'<field.*value="(.*?)"')
NAME_FROM_OBJ = re.compile(r'<field.*name="(.*?)"')
POS_FROM_OBJ = re.compile(r'<field.*pos="(.*?)"')
SHOWNAME_FROM_OBJ = re.compile(r'<field.*showname="(.*?)"')
IP_FROM_OBJ = re.compile(r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b")


class Parser(object):
    def __init__(self, infile, outfile, tcname):
        self.prevnode = None
        self.temp_binary = None
        self.temp_name = None
        self.of = []
        self.infile = infile
        self.outfile = outfile
        self.tcname = tcname
        self.xmldoc = None

    def handle_file(self):
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
        with open(self.outfile, 'w') as output_file:
            for line in self.of:
                output_file.write(line)

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
        self.of.append("Test Setup      UDP Server and Client are initialized in port ${GTP_CONTROL_PORT}\n")
        self.of.append("Test Teardown   Close Connections\n")
        self.of.append("Default Tags    regression\n")
        self.of.append("Library         rammbock.Rammbock\n")
        self.of.append("Resource        ../resources/Messaging.txt\n")
        self.of.append("Resource        ../protocols/gtp/v2.txt\n")
        self.of.append("\n")
        self.of.append("*** Variables ***\n")
        self.of.append("${GTP_CONTROL_PORT}=    2123\n")
        self.of.append("\n")

    def _handle_node(self, node):
        if not node.toxml().startswith('\n'):
            length = self._length(node)
            if length is 1 or not node.childNodes:
                if self._pos(node) == self._pos(self.prevnode) and self._name(self.prevnode):
                    self._add_binary(node)
                    self.prevnode = node
                else:
                    if self.temp_name:
                        self.of.append("    Add Decimal As Binary    " + str(self.temp_binary) + "    " + str(self._length(self.prevnode)) + "    #" + self.temp_name + "\n")
                        self.temp_name = None 
                        self.temp_binary = None
                    if not self._name(node):
                        to_add = "    Add Decimal As Binary    " + self._value(node) + "    " + str(length) + "    #" + self._show(node) + "\n"
                    else:
                        if IP_FROM_OBJ.match(self._show(node)):
                            to_add = "    Add Ip As Hex    " + self._show(node) + "    #" + self._name(node) + "\n"
                        else:
                            to_add = "    Add Decimal As Binary    " + self._show(node) + "    " + str(length) + "    #" + self._name(node) + "\n"
                    self.of.append(to_add)
                    self.prevnode = node
            else:
                if self._name(node):
                    self.prevnode = node
                for subnode in node.childNodes:
                    self._handle_node(subnode)

    def _add_binary(self, node):
        if not self.temp_name:
            self.of = self.of[:-1]
            self.temp_name = self._name(self.prevnode)
            self.temp_binary = self._showname_bin(self.prevnode)
        self.temp_name += ', ' + self._name(node)
        self.temp_binary += self._showname_bin(node)

    def _showname_bin(self, node):
        showname = SHOWNAME_FROM_OBJ.match(node.toxml()).group(1)
        try:
            return int(showname[:9].replace('.','0').replace(' ', ''), 2)
        except ValueError:
            return int(SHOW_FROM_OBJ.match(node.toxml()).group(1))

    def _length(self, node):
        if not node:
            return -1
        return int(LENGTH_FROM_OBJ.match(node.toxml()).group(1))

    def _show(self, node):
        return SHOW_FROM_OBJ.match(node.toxml()).group(1)

    def _value(self, node):
        return VALUE_FROM_OBJ.match(node.toxml()).group(1)

    def _name(self, node):
        if not node:
            return ""
        return NAME_FROM_OBJ.match(node.toxml()).group(1)

    def _pos(self, node):
        if not node:
            return "-1"
        return POS_FROM_OBJ.match(node.toxml()).group(1)

if __name__ == "__main__":
    if len(argv) is 4:
        Parser(argv[1], argv[2], argv[3]).handle_file()
    else:
        print "Usage: python wiresharkXMLParser.py infile.xml outfile.txt test\\ case\\ name"
