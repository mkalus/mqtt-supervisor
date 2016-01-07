# Service calling a command and expecting certain return values

import os
from .ServiceClass import ServiceClass
import subprocess

"""
services:
  # name of service
  apache:
    type: CommandReturnService
    # check frequency in seconds
    check_frequency: 60
    # always send update, not just on value changes
    always_send_update: false
    # run command
    command: "service apache2 status"
    command_shell: true
    return_value_ok: 0
    # or check fails only
    #return_value_fail: 3
    value_if_ok: 1
    value_if_fail: 0
    # or take return value as message value
    #return_value_as_message_value: false
    topic_value: status
    qos_value: 0
    retain_value: false
    add_time: true
    topic_time: time
    qos_time: 0
    retain_time: false
"""


class CommandReturnService(ServiceClass):
    devnull = open(os.devnull, 'w')

    def __init__(self, name, config, settings):
        super(CommandReturnService, self).__init__(name, config, settings)
        # command to execute
        self.command = self._get_from_config(config, "command")
        # boolean, true if shell should be used
        self.command_shell = self._get_from_config(config, "command_shell", True)
        # one of these both should exist!
        self.return_value_ok = self._get_from_config(config, "return_value_ok")
        self.return_value_fail = self._get_from_config(config, "return_value_fail")
        # or take return value as message value
        self.return_value_as_message_value = self._get_from_config(config, "return_value_as_message_value", False)

    # return status value of this class
    def _get_status_value(self):
        return subprocess.call(self.command, shell=self.command_shell, stdout=CommandReturnService.devnull, stderr=CommandReturnService.devnull)

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
        return service_name == "CommandReturnService"
