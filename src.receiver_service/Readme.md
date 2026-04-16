UDP/TCP-Receiver Service
========================

This is a simple implementation of a central UDP/TCP receiver-service.
It listens on a port and accepts csv-data as UDP-packets or TCP-packets.

Senders can be dataloggers (using the
[send_udp or send_tcp](../docs/core_config_tasks.md) tasks) or a gateway (using
one of the `GW_TX_TYPE`s [`UDP`, `TCP` or `IFX`](../docs/gateway_config.md)).

The service is configurable and executes a list of tasks for every
record it receives.


Available Tasks
---------------

| Name                        | Description                               |
|-----------------------------|-------------------------------------------|
| noop                        | dummy task that does nothing              |
| print                       | print record (with text conversion)       |
| save                        | save record in binary format              |
| ifx_load                    | load data to an InfluxDB                  |


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

The central configuration file is `/var/lib/datalogger/datalogger.conf`.
