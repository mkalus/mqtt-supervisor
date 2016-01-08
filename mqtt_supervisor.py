#!/usr/bin/env python3
# -*- coding: utf-8 -*
# Supervisor process - reads config.yaml and checks services

# installation on Ubuntu
# sudo apt-get install python-yaml
# sudo pip3 install paho-mqtt
#
# or (if running python 2.7):
# sudo pip install paho-mqtt
# + backport of ipaddress to python 2.7:
# sudo apt-get install python-ipaddress
#
# If your user has trouble accessing paho-mqtt, execute the following commands:
# sudo find /usr/local/lib/python3.4/dist-packages/ -type d -exec chmod 755 {} ';'
# sudo find /usr/local/lib/python3.4/dist-packages/ -type f -exec chmod 644 {} ';'

import logging
import services
import sched
import time
import sys
import yaml

import paho.mqtt.client as paho

logging.basicConfig(level=logging.INFO)


# read yaml configuration
def read_configuration(file='config.yaml'):
    logging.info("Opening config file " + file)
    with open(file, 'r') as myfile:
        data = myfile.read()
    return yaml.load(data)


try:
    config = read_configuration()
except Exception as e:
    print("Could not read configuration: " + str(e))
    sys.exit(1)

# open mqtt client
client = paho.Client()

# set user/password
if config['mqtt_broker']['use_username_password']:
    client.username_pw_set(config['mqtt_broker']['username'], config['mqtt_broker']['password'])

# set tls
if config['mqtt_broker']['use_ca']:
    client.tls_set(config['mqtt_broker']['ca_cert'])
    client.tls_insecure_set(config['mqtt_broker']['ca_insecure'])

# connect
try:
    client.connect(config['mqtt_broker']['hostname'], config['mqtt_broker']['port'], config['mqtt_broker']['keepalive'])
    logging.info("Connected to broker " + config['mqtt_broker']['hostname'] + ":" + str(config['mqtt_broker']['port']))
except Exception as e:
    print("Could not connect with mqtt broker: " + str(e))
    sys.exit(1)

# add client to config
config['settings']['mqtt_client'] = client


# define check function to run on scheduler
def check_service(service, sc):
    logging.info("Running " + service.name)
    service.execute()

    # re-enter service
    sc.enter(service.check_frequency, 1, check_service, (service, sc,))


# initialize scheduler
s = sched.scheduler(time.time, time.sleep)

# get services and add them to scheduler
for key, service_config in config['services'].items():
    service = services.service_factory(service_config['type'], key, service_config, config['settings'])

    # add to scheduler
    s.enter(0, 1, check_service, (service, s,))

# run scheduler
s.run()
