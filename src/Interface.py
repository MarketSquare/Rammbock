import subprocess
import re
from random import randint
from sys import platform
find_ip_regexp = re.compile(r'.*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')

OSX = ['darwin']
LINUX = ['linux2', 'linux']
WINDOWS = ['win32']

def get_ip_address(ifname):
    """
    Returns ip address from local machine. interface name is given as an parameter.
    get_ip_address | <interface>
    e.g. get_ip_address | eth0
    """
    process = subprocess.Popen(_get_ifconfig_cmd("show", ifname), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = process.communicate()[0]
    return _return_ip_address_from_ifconfig_output(output)

def create_interface_alias(ifname, ip, netmask):
    """ Creates interface """
    virtual_if_name = _get_free_interface_alias(ifname)
    print "ifconfig", virtual_if_name, ip, "netmask", netmask
    process = subprocess.Popen(_get_ifconfig_cmd("add", virtual_if_name, ip, netmask), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()
    return virtual_if_name

def check_interface(ifname):
    """Checks if interface have ip address. Returns False or True"""
    ipaddress= get_ip_address(ifname)
    print "ipaddress=" + ipaddress 
    return ipaddress != ""

def check_interface_for_ip(ifname, ip):
    """checks given network interface for given ip address"""
    process = subprocess.Popen(_get_ifconfig_cmd("show", ifname), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = process.communicate()[0]
    ips=_return_ip_addresses_from_ifconfig_output(output)
    return ip in ips

def del_alias(ifname, ip):
    """Deletes this interface"""
    print "ifconfig", ifname, "down"
    process = subprocess.Popen(_get_ifconfig_cmd("del", ifname, ip), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()

def _return_ip_addresses_from_ifconfig_output(output):
    addresses = []
    for line in output.split('\n'):
        if 'inet ' in line or 'IPv4 Address' in line or 'IP Address' in line:
            ipAddress = find_ip_regexp.match(line).group(1)
            print "ip address is:" + ipAddress
            addresses.append(ipAddress)
    return addresses

def _return_ip_address_from_ifconfig_output(output):
    addresses = _return_ip_addresses_from_ifconfig_output(output)
    if addresses == []:
        return ''
    else:
        return addresses[0]

def _get_free_interface_alias(ifname):
    if platform in OSX or platform in WINDOWS:
        return ifname
    else:
        while True:
            virtual_if_name = ifname + ":" + str(randint(1, 10000))
            if not check_interface(virtual_if_name):
                return virtual_if_name

def _get_ifconfig_cmd(cmd, ifname, ip=None, netmask=None):
    returnable = _get_base_ifcmd()
    if cmd == "add":
        re = returnable + _get_add_cmd(ifname, ip, netmask)
    elif cmd == "del":
        re = returnable + _get_del_cmd(ifname, ip)
    elif cmd == "show":
        re = returnable + _get_show_cmd(ifname)
    print re
    return re

def _get_base_ifcmd():
    if platform in OSX:
        return ['/sbin/ifconfig']
    elif platform in WINDOWS:
        return ['netsh', 'interface', 'ipv4']
    else:
        return ['/sbin/ifconfig']

def _get_add_cmd(ifname, ip, netmask):
    if platform in OSX:
        return [ifname, 'alias', ip, "netmask", netmask]
    elif platform in WINDOWS:
        return ["add", "address", ifname, ip, netmask]
    elif platform in LINUX:
        return [ifname, ip, "netmask", netmask]

def _get_del_cmd(ifname, ip):
    if platform in OSX:
        return [ifname, '-alias', ip]
    elif platform in WINDOWS:
        return ["delete", "address", ifname, ip]
    elif platform in LINUX:
        return [ifname, "down"]

def _get_show_cmd(ifname):
    if platform in WINDOWS:
        return ["show", "config", ifname]
    else:
        return [ifname]
