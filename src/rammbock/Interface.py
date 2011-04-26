import os
import subprocess
import re

def PhysicalInterface(int_alias, ifname, ip_address=None, Netmask=None):
    return Interface().create_physical_interface(int_alias, ifname, ip_address=ip_address, Netmask=Netmask)

def VirtualInterface(int_alias, ifname, ip_address, netmask):
    return Interface().create_virtual_interface(int_alias, ifname, ip_address, netmask)

def get_ip_address(ifname):
    """
    Returns ip address from local machine. interface name is given as an parameter.
    get_ip_address | <interface>
    e.g. get_ip_address | eth0
    """
    process = subprocess.Popen(['/sbin/ifconfig', ifname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = process.communicate()[0]
    for line in output.split('\n'):
        if 'inet addr:' in line:
            ipAddress = re.compile('addr\:([^\s]+)\s').search(line).group(1)
            print "ip address is:" + ipAddress
            return ipAddress
    return ''

class Interface(object):

    def __init__(self):
        self.ifname = ""
        self.ifUp = False
        self.ifIpAddress =""

    def create_virtual_interface(self, int_alias, ifname, ip_address, netmask):
        """ Creates interface """
        if_ip_address = "1"
        i = 1
        while if_ip_address != "":
            virtual_if_name = ifname + ":" + str(i)
            if_ip_address = get_ip_address(virtual_if_name)
            if if_ip_address == "":
                subprocess.Popen(["ifconfig", virtual_if_name, ip_address, "netmask", netmask], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.ifname = virtual_if_name
                if self.check_interface():
                    self.ifIpAddress = get_ip_address(virtual_if_name)
                    self.ifUp = True
                    return self
                else:
                    self.ifname = ""
                    raise Exception("Creating new Virtual interface failed. Probably physical interface: "+ifname)
            else:
                i = i + 1
        return self

    def create_physical_interface(self, int_alias, ifname, ip_address = None, Netmask = None):
        self.ifname = ifname
        if self.check_interface():
            self.ifIpAddress = get_ip_address(ifname)
            self.ifUp = True
            return self
        else:
            raise Exception("Tried to use physical interface: "+ifname+" probably does not exist")

    def check_interface(self):
        """Checks if interface have ip address. Returns False or True"""
        ipaddress= get_ip_address(self.ifname)
        print "ipaddress=" + ipaddress 
        return ipaddress != ""

    def del_interface(self):
        """Deletes this interface"""
        subprocess.Popen(["ifconfig", self.ifname, "down"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.ifUp = False
