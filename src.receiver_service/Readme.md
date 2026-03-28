UDP/TCP-Receiver Service
========================

This is a simple implementation of a central UDP/TCP receiver-service.
It listens on a port and accepts csv-data as UDP-packets or TCP-packets.

Senders can be dataloggers (using the
[send_udp](../docs/core_config_tasks.md) task) or a datalogger (using
the [GW_TX_TYPE `UDP`](../docs/gateway_config.md)).

The service is configurable and executes a list of tasks for every
record it receives.


Installation
------------

The service is a Python3-script and does not need any additional software.
Use the following steps to install the service:

    cd src.receiver_service/tools
    sudo tools/install

This will create a systemd-service and enable it. To start it, either reboot
or just run

    sudo systemctl start datalogger_receiver.service


Configuration
-------------

The central configuration file is `/etc/datalogger.conf`.
