import subprocess
import re
from sys import platform
find_ip_regexp = re.compile(r'.*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')

OSX = ['darwin']
LINUX = ['linux2', 'linux']
WINDOWS = ['win32']
_created_aliases = set()

def get_ip_address(ifname):
    """
    Returns ip address from local machine. interface name is given as an parameter.
    get_ip_address | <interface>
    e.g. get_ip_address | eth0
    """
    ip = _get_ip_addresses_for_ifname(ifname)
    if ip:
        return ip[0]
    return None

def create_interface_alias(ifname, ip, netmask):
    """ Creates interface """
    virtual_if_name = _get_free_interface_alias(ifname)
    print "ifconfig", virtual_if_name, ip, "netmask", netmask
    process = _get_ifconfig_cmd("add", virtual_if_name, ip, netmask)
    process.wait()
    _created_aliases.add((virtual_if_name, ip))
    return virtual_if_name

def interface_should_have_an_ip_address(ifname):
    """Verifies that interface has an ip address."""
    if not get_ip_address(ifname):
        raise AssertionError("Interface %s does not have an ip address." % ifname)

def interface_should_have_ip(ifname, ip):
    """Verifies that given network interface has given ip address"""
    if ip not in _get_ip_addresses_for_ifname(ifname):
        raise AssertionError("interface %s does not have ip %s" % (ifname, ip))

def interface_should_not_have_ip(ifname, ip):
    """Verifies that given network interface does not have given ip address"""
    if ip in _get_ip_addresses_for_ifname(ifname):
        raise AssertionError("interface %s has ip %s" % (ifname, ip))

def del_alias(if_name, ip):
    """Deletes this interface"""
    process = _get_ifconfig_cmd("del", if_name, ip)
    process.wait()
    _created_aliases.remove((if_name, ip))

def del_all_aliases():
    for if_name, ip in list(_created_aliases):
        del_alias(if_name, ip)

def _get_ip_addresses_for_ifname(ifname):
    process = _get_ifconfig_cmd("show", ifname)
    output = process.communicate()[0]
    addresses = []
    for line in output.split('\n'):
        if 'inet ' in line or 'IPv4 Address' in line or 'IP Address' in line:
            ipAddress = find_ip_regexp.match(line).group(1)
            print "ip address is:" + ipAddress
            addresses.append(ipAddress)
    return addresses

def _get_free_interface_alias(ifname):
    if platform in OSX or platform in WINDOWS:
        return ifname
    for i in range(10000):
        virtual_if_name = ifname + ":" + str(i)
        if not get_ip_address(virtual_if_name):
            return virtual_if_name
    raise AssertionError("No free interface alias in range %s:1 - %s:10000" %
                         (ifname, ifname))

def _get_ifconfig_cmd(cmd, ifname, ip=None, netmask=None):
    returnable = _get_base_ifcmd()
    if cmd == "add":
        re = returnable + _get_add_cmd(ifname, ip, netmask)
    elif cmd == "del":
        re = returnable + _get_del_cmd(ifname, ip)
    elif cmd == "show":
        re = returnable + _get_show_cmd(ifname)
    print re
    return subprocess.Popen(re, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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
