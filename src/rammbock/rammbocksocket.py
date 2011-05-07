import fcntl
import struct
import socket


def _get_ip_address(rsocket, ifname):
    ifname=str(ifname)
    print ifname
    return socket.inet_ntoa(fcntl.ioctl(
        rsocket.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])