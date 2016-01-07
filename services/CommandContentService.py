# Service calling a command and checking output for a certain regex

import re
from .ServiceClass import ServiceClass
import subprocess

"""
services:
  # name of service
  cpu0:
    type: CommandContentService
    # check frequency in seconds
    check_frequency: 10
    # always send update, not just on value changes
    always_send_update: true
    # run command
    command: "cpufreq-info -c 0 -fm"
    # regex to look for - if it is empty, take output of whole command as return value
    regexp:
    # replace output with regexp, only makes sense if regexp is empty
    regexp_sub: '[\s+]'
    regexp_sub_with: ''
    #value_if_ok: 1
    #value_if_fail: 0
    # or take return value as message value
    #return_value_as_message_value: false
    return_value_as_message_value: true
    retain_value: false
    retain_time: false
"""


class CommandContentService(ServiceClass):
    def __init__(self, name, config, settings):
        super(CommandContentService, self).__init__(name, config, settings)
        # command to execute
        self.command = self._get_from_config(config, "command")
        # boolean, true if shell should be used
        self.command_shell = self._get_from_config(config, "command_shell", True)
        # regex to check
        self.regexp = self._get_from_config(config, "regexp")
        self.regexp_sub = self._get_from_config(config, "regexp_sub")
        self.regexp_sub_with = self._get_from_config(config, "regexp_sub_with", "")
        # one of these both should exist!
        self.return_value_ok = self._get_from_config(config, "return_value_ok")
        self.return_value_fail = self._get_from_config(config, "return_value_fail")
        # or take return value as message value
        self.return_value_as_message_value = self._get_from_config(config, "return_value_as_message_value", False)
        # pre-compile regexes
        if self.regexp is not None:
            self.r = re.compile(self.regexp)
        else:
            self.r = None
        if self.regexp_sub is not None:
            self.rs = re.compile(self.regexp_sub)
        else:
            self.rs = None

    # return status value of this class
    def _get_status_value(self):
        output = str(subprocess.check_output(self.command, shell=self.command_shell))
        # just match output?
        if self.r is not None:
            return self.r.match(output)
        # replace output?
        if self.rs is not None:
            return self.rs.sub(self.regexp_sub_with, output)
        # whole output
        return output

    # return message value for message updates
    def _get_message_value(self):
        if self.return_value_as_message_value:
            return self.last_value
        # get new return value
        if self.return_value_ok is not None:
            if self.last_value == self.return_value_ok:
                return self.value_if_ok
            else:
                return self.value_if_fail
        else:
            if self.return_value_fail is not None:
                if self.last_value == self.return_value_fail:
                    return self.value_if_fail
                else:
                    return self.value_if_ok
        # no valid config: no value - no message
        return None

    @classmethod
    def is_service_name_for(cls, service_name):
        return service_name == "CommandContentService"
