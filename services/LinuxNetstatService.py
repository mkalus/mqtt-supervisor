# Service checking linux' netstat directory for certain ports

import ipaddress
import re
from ServiceClass import ServiceClass
import socket

"""
services:
  # name of service
  ssh:
    type: LinuxNetstatService
    # check frequency in seconds
    check_frequency: 60
    # always send update, not just on value changes
    always_send_update: false
    ip6: false
    udp: false
    host: None
    port: 22
    value_if_ok: 1
    value_if_fail: 0
    topic_value: status
    qos_value: 0
    retain_value: false
    add_time: true
    topic_time: time
    qos_time: 0
    retain_time: false

"""


class LinuxNetstatService(ServiceClass):
    def __init__(self, name, config, settings):
        super(LinuxNetstatService, self).__init__(name, config, settings)
        # main values
        self.ip6 = self._get_from_config(config, "ip6", False)
        self.udp = self._get_from_config(config, "udp", False)
        self.host = self._get_from_config(config, "host", None)
        self.port = self._get_from_config(config, "port")
        # preformat stuff
        if self.host is None:
            self.hex_host = '[0-9A-F]+' # any regexp
        else:
            self.hex_host = self._host_to_hex(self.host)
        if self.port is None:
            self.hex_port = '[0-9A-F]+' # any regexp
        else:
            self.hex_port = self._port_to_hex(self.port)
        # what do we look for? compile regex for later on
        self.regexp = re.compile('^\s*\d+:\s*' + self.hex_host + ':' + self.hex_port + '\s+')

    # calculate hex from hostname/ip address
    def _host_to_hex(self, host):
        # try to parse as address
        try:
            address = ipaddress.ip_address(unicode(host, "utf-8"))
        except ValueError:
            # try to get ip by host name
            address = None
            for tuple in socket.getaddrinfo(host, None):
                # ip6 and network type 10
                if self.ip6 and tuple[0] == 10:
                    address = tuple[4][0]
                    break
                # ipv4 and network type 2
                if not self.ip6 and tuple[0] == 2:
                    address = tuple[4][0]
                    break
            # try to parse again
            address = ipaddress.ip_address(unicode(address, "utf-8"))
        # pack ip, invert it and encode to hex
        if self.ip6: # ipv6 is reversed in blocks of 4 bytes
            tempaddress = address.packed[::-1].encode("hex").upper()
            return tempaddress[24:32] + tempaddress[16:24] + tempaddress[8:16] + tempaddress[0:8]
        return address.packed[::-1].encode("hex").upper()

    # calculate hex from port number
    def _port_to_hex(self, port):
        return hex(port)[2:].upper().zfill(4)

    # check an input line for pattern above
    def _check_line(self, line):
        if self.regexp.match(line):
            return True
        return False

    # find possible line in netstat
    def _find_line(self):
        # determine correct path
        path = "/proc/net/"
        if self.udp:
            path += "udp"
        else:
            path += "tcp"
        if self.ip6:
            path += "6"
        # load each line and analyze it
        f = open(path, 'r')
        for line in f.readlines():
            if self._check_line(line):
                return True
        # fallback
        return False

    # return status value of this class
    def _get_status_value(self):
        # call netstat stuff and check lines
        return self._find_line()

    # return message value for message updates
    def _get_message_value(self):
        if self.last_value:
            return self.value_if_ok
        else:
            return self.value_if_fail

    @classmethod
    def is_service_name_for(cls, service_name):
        return service_name == "LinuxNetstatService"
