from xml.dom import minidom
from sys import argv
from time import asctime
import re


LENGTH_FROM_OBJ = re.compile(r'<field.*size="(\w*)"')
SHOW_FROM_OBJ = re.compile(r'<field.*show="(.*?)"')
VALUE_FROM_OBJ = re.compile(r'<field.*value="(.*?)"')
NAME_FROM_OBJ = re.compile(r'<field.*name="(.*?)"')

def parse_file(infile, outfile, tcname):
    of = open(outfile, 'w')
    _append_meta_information(of, tcname)
    xmldoc = minidom.parse(infile)
    root = xmldoc.childNodes[0]
    for node in root.childNodes:
        _handle_node(node, of)
    of.write("    Client Sends Data\n")
    of.close()

def _append_meta_information(of, tcname):
    of.write("*** Settings ***\n")
    of.write("[Documentation]    This test file has been generated automatically with PDML to Robot framework test case converter (WiresharkXMLParser.py) at " + asctime() + ".\n")
    of.write("Test Setup      UDP Server and Client are initialized\n")
    of.write("Test Teardown   Close Connections\n")
    of.write("Default Tags    regression\n")
    of.write("Library         rammbock.Rammbock\n")
    of.write("Resource        ../resources/Messaging.txt\n")
    of.write("Resource        ../protocols/gtp/v2.txt\n")
    of.write("\n")
    of.write("*** Test Cases ***\n")
    of.write(tcname + '\n')
    of.write("    Create Message\n")

def _handle_node(node, of):
    if not node.toxml().startswith('\n'):
        length = _length(node)
        if length is 1 or len(node.childNodes) is 0:
            if _name(node) == "":
                to_add = "    Add Decimal As Binary    " + _value(node) + "    " + str(_length(node)) + "    #" + _show(node) +"\n"
            else:
                to_add = "    Add Decimal As Binary    " + _show(node) + "    " + str(_length(node)) + "    #" + _name(node) +"\n"
            of.write(to_add)
        elif len(node.childNodes) > 0:
            for subnode in node.childNodes:
                _handle_node(subnode, of)

def _length(node):
    return int(LENGTH_FROM_OBJ.match(node.toxml()).group(1))

def _show(node):
    return SHOW_FROM_OBJ.match(node.toxml()).group(1)

def _value(node):
    return VALUE_FROM_OBJ.match(node.toxml()).group(1)

def _name(node):
    return NAME_FROM_OBJ.match(node.toxml()).group(1)

if __name__ == "__main__":
    if len(argv) is 4:
        parse_file(argv[1], argv[2], argv[3])
    else:
        print "Usage: python wiresharkXMLParser.py infile.xml outfile.txt test\\ case\\ name"
