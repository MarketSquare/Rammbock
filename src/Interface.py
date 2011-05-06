import subprocess
import re
from random import randint

def get_ip_address(ifname):
    """
    Returns ip address from local machine. interface name is given as an parameter.
    get_ip_address | <interface>
    e.g. get_ip_address | eth0
    """
    process = subprocess.Popen(['/sbin/ifconfig', ifname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = process.communicate()[0]
    return __return_ip_address_from_ifconfig_output(output)

def __return_ip_address_from_ifconfig_output(output):
    for line in output.split('\n'):
        if 'inet addr:' in line:
            ipAddress = re.compile('addr\:([^\s]+)\s').search(line).group(1)
            print "ip address is:" + ipAddress
            return ipAddress
    return ''

def create_interface_alias(ifname, ip_address, netmask):
    """ Creates interface """
    virtual_if_name = ifname + ":" + str(randint(1000, 10000))
    print "ifconfig", virtual_if_name, ip_address, "netmask", netmask
    process = subprocess.Popen(["ifconfig", virtual_if_name, ip_address, "netmask", netmask], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()
    return virtual_if_name

def check_interface(ifname):
    """Checks if interface have ip address. Returns False or True"""
    ipaddress= get_ip_address(ifname)
    print "ipaddress=" + ipaddress 
    return ipaddress != ""

def del_interface(ifname):
    """Deletes this interface"""
    process = subprocess.Popen(["ifconfig", ifname, "down"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()