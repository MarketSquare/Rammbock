import os
class Interface:

    def __init__(self):
        self.ifname = ""
        self.ifUp = False
        self.ifIpAddress =""

    def create_virtual_interface(self, int_alias, ifname, ip_address, netmask):
        """ Creates interface """
        if_ip_address = "1"
        i = 1
        while if_ip_address  != "":
            virtual_if_name = ifname + ":" + str(i)
            if_ip_address = self.get_ip_address(virtual_if_name)
            if if_ip_address == "":
                command = "ifconfig " + virtual_if_name + " " + ip_address + " netmask " + netmask
                os.popen(command)
                self.ifname = virtual_if_name
                if self.check_interface():
                    self.ifIpAddress = self.get_ip_address(virtual_if_name)
                    self.ifUp = True
                    return self
                else:
                    self.ifname = ""
                    raise Exception("Creating new Virtual interface failed")
            else:
                i = i + 1
        return self

    def create_physical_interface(self, int_alias, ifname, ip_address = None, Netmask = None):
         self.ifname = ifname
         if self.check_interface():
              self.ifIpAddress = self.get_ip_address(ifname)
              self.ifUp = True
              return self
         else:
              raise Exception("Tried to use physical interface: "+ifname+" probably does not exist")

    def check_interface(self):
        """Checks if interface have ip address. Returns False or True"""
        ipaddress= self.get_ip_address(self.ifname)
        print "ipaddress=" + ipaddress 
        if ipaddress != "":
            return True
        else:
            return False

    def del_interface(self):
        """Deletes this interface"""
        os.popen("ifconfig " + self.ifname + " down")
        self.ifUp = False

    def get_ip_address(self, ifname):
        """
        Returns ip address from local machine. interface name is given as an parameter.
        get_ip_address | <interface>
        e.g. get_ip_address | eth0
        """
        command =  "/sbin/ifconfig " + ifname + " | grep inet | awk '{print $2}' | sed -e s/.*://"
        try:
             ipAddressList = os.popen(command).readlines()
        except Error, e:
             print type(e)
             raise
        ipAddress = "".join(ipAddressList)
        ipAddress = ipAddress.strip()
        print "ip address is:" + ipAddress
        return ipAddress 
