import subprocess
import re
from random import randint

def PhysicalInterface(int_alias, ifname, ip_address=None, Netmask=None):
    return Interface()._create_physical_interface(int_alias, ifname, ip_address=ip_address, Netmask=Netmask)

def VirtualInterface(int_alias, ifname, ip_address, netmask):
    return Interface()._create_virtual_interface(int_alias, ifname, ip_address, netmask)

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

    def _create_virtual_interface(self, int_alias, ifname, ip_address, netmask):
        """ Creates interface """
        if_ip_address = "1"
        while if_ip_address != "":
            virtual_if_name = ifname + ":" + str(randint(1000, 10000))
            if_ip_address = get_ip_address(virtual_if_name)
            if if_ip_address == "":
                process = subprocess.Popen(["ifconfig", virtual_if_name, ip_address, "netmask", netmask], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.ifname = virtual_if_name
                if process.wait() == 0:
                    self.ifIpAddress = get_ip_address(virtual_if_name)
                    self.ifUp = True
                    return self
                else:
                    print 'WARN virtual_if_name '+virtual_if_name
                    try:
                        self.del_interface()
                    except Exception:
                        pass
                    self.ifname = ""
                    raise Exception("Creating new Virtual interface failed. Probably physical interface: "+ifname)
        return self

    def _create_physical_interface(self, int_alias, ifname, ip_address = None, Netmask = None):
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
        process = subprocess.Popen(["ifconfig", self.ifname, "down"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.ifUp = process.wait() != 0
        if self.ifUp:
            raise Exception('Could not delete interface '+self.ifname)
