import subprocess
import re
from random import randint
from sys import platform


OSX = 'darwin'
LINUX = 'linux2'
WINDOWS = 'win32'

def get_ip_address(ifname):
    """
    Returns ip address from local machine. interface name is given as an parameter.
    get_ip_address | <interface>
    e.g. get_ip_address | eth0
    """
    process = subprocess.Popen([__get_ifconfig_cmd(), ifname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = process.communicate()[0]
    return __return_ip_address_from_ifconfig_output(output)

def create_interface_alias(ifname, ip_address, netmask):
    """ Creates interface """
    virtual_if_name = __get_free_interface_alias(ifname)
    print "ifconfig", virtual_if_name, ip_address, "netmask", netmask
    if platform == OSX:
        process = subprocess.Popen([__get_ifconfig_cmd(), virtual_if_name, 'alias', ip_address, "netmask", netmask], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        process = subprocess.Popen([__get_ifconfig_cmd(), virtual_if_name, ip_address, "netmask", netmask], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()
    return virtual_if_name

def check_interface(ifname):
    """Checks if interface have ip address. Returns False or True"""
    ipaddress= get_ip_address(ifname)
    print "ipaddress=" + ipaddress 
    return ipaddress != ""

def check_interface_for_ip(ifname, ip):
    """checks given network interface for given ip address"""
    process = subprocess.Popen([__get_ifconfig_cmd(), ifname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = process.communicate()[0]
    ips=__return_ip_addresses_from_ifconfig_output(output)
    print ips
    return ip in ips

def del_alias(ifname, ip):
    """Deletes this interface"""
    print "ifconfig", ifname, "down"
    if platform == OSX:
        process = subprocess.Popen([__get_ifconfig_cmd(), ifname, '-alias', ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        process = subprocess.Popen([__get_ifconfig_cmd(), ifname, "down"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    process.wait()

def __return_ip_addresses_from_ifconfig_output(output):
    addresses = []
    for line in output.split('\n'):
        if 'inet ' in line or 'IPv4 Address' in line:
            ipAddress = re.match(r'.*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line).group(1) 
            print "ip address is:" + ipAddress
            addresses.append(ipAddress)
    return addresses

def __return_ip_address_from_ifconfig_output(output):
    addresses = __return_ip_addresses_from_ifconfig_output(output)
    if addresses == []:
        return ''
    else:
        return addresses[0]

def __get_free_interface_alias(ifname):
    if platform == 'darwin':
        return ifname
    else:
        while True:
            virtual_if_name = ifname + ":" + str(randint(1, 10000))
            if not check_interface(virtual_if_name):
                return virtual_if_name

def __get_ifconfig_cmd():
    if platform == OSX:
        return '/sbin/ifconfig'
    elif platform == WINDOWS:
        return 'ipconfig'
    else:
        return '/sbin/ifconfig'
