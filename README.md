# mqtt-supervisor
Python based service checker that dispatches status events to an MQTT broker.

Configuration is set by a YAML file in which you can define any number of services to supervise. Software supports:
* MQTT quality of service (QOS)
* TLS/SSL-Certificates
* MQTT user/password authentication

There are three types of service supervision types available right now:

* **CommandReturnService:** Run a command and check its return value.
* **CommandContentService:** Run a command and either take its output as value of check the output via Regular
Expression.
* **LinuxNetstatService:** Check `/proc/net/tcp` or `/proc/net/tcp6` for certain ports / hosts listing. Works on Linux
only.

(c) 2016 Maximilian Kalus (www.auxnet.de)