# Service base class

import datetime
import logging


class ServiceClass(object):
    def __init__(self, name, config, settings):
        self.name = name
        self.check_frequency = self._get_from_config(config, 'check_frequency', 60)
        self.always_send_update = self._get_from_config(config, 'always_send_update', False)
        self.settings = settings
        self.mqtt_client = self._get_from_config(settings, 'mqtt_client')
        # other values, might be empty
        self.value_if_ok = self._get_from_config(config, "value_if_ok", 1)
        self.value_if_fail = self._get_from_config(config, "value_if_fail", 0)
        self.topic_value = self._get_from_config(config, "topic_value", "status")
        self.qos_value = self._get_from_config(config, "qos_value", 0)
        self.retain_value = self._get_from_config(config, "retain_value", True)
        self.add_time = self._get_from_config(config, "add_time", True)
        self.topic_time = self._get_from_config(config, "topic_time", "time")
        self.qos_time = self._get_from_config(config, "qos_time", 0)
        self.retain_time = self._get_from_config(config, "retain_time", True)
        # last return value
        self.last_value = None

    # dispatch mqtt message
    def dispatch_message(self, topic, value, qos, retain):
        logging.info("Dispatching new message " + topic + " with value " + str(value))
        self.mqtt_client.publish(topic, value, qos, retain)

    # dispatch mqtt message with certain value
    def _dispatch_message_with_value(self, message_value):
        # dispatch mqtt message if there is a value
        if message_value is not None:
            topic_value = self.settings['mqtt_base_topic'] + '/' + self.name
            if self.topic_value is not None:
                topic_value += '/' + self.topic_value
            self.dispatch_message(topic_value, message_value, self.qos_value, self.retain_value)
            if self.add_time and self.topic_time is not None:
                topic_value = self.settings['mqtt_base_topic'] + '/' + self.name + '/' + self.topic_time
                message_value = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.dispatch_message(topic_value, message_value, self.qos_time, self.retain_time)

    # return status value of this class
    # to be overwritten by child classes
    def _get_status_value(self):
        return 0

    # return message value for message updates
    # to be overwritten by child classes
    def _get_message_value(self):
        return 1

    # execute service
    def execute(self):
        # get new status value
        status_value = self._get_status_value()
        # if value is sent always or if value unlike last one
        if self.always_send_update or status_value != self.last_value:
            self.last_value = status_value
            # get new message value
            message_value = self._get_message_value()
            # dispatch message
            self._dispatch_message_with_value(message_value)

    # get a key from config of load default
    @staticmethod
    def _get_from_config(config, key, default=None):
        try:
            return config[key]
        except (IndexError, KeyError, TypeError):
            return default
