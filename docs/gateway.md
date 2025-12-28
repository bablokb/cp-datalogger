Gateway
=======

The gateway is an optional central component for a network of dataloggers.
A gateway will *receive* data from the dataloggers (i.e. from downstream)
and *transmit* data to an upstream location. This second step is optional.

There are three components on every gateway:

  - The receiver: on the hardware side, this is a technology component
    like a LoRa-chip (or WLAN, BLE ...). On the software side, this is
    a class that implements a certain interface (e.g. a receive()-method).
  - The transmitter: this is similar to the receiver but used to send
    data upstream.
  - The gateway-MCU itself providing configuration and the framework for
    running the gateway.

Like dataloggers, the gateway can run continuously or in intervals. While
active, the gateway runs a receive-process loop. The receive part
queries the receiver for new packets, the process part runs a number of
configured tasks for the data (tranmitting is one task of many).


Implementations
---------------

One implementation uses [Blues](https://dev.blues.io). Blues provides
a LTE/GSM-chip in a special hardware package suitable for data-transfer into
the cloud.

A simpler implementation just runs on the normal datalogger hardware. In
this case, there is no upstreaming of data, but the data is collected
and stored centrally on the XTSD-card of the datalogger.


Software
--------

See [Application Firmware](./software_gateway.md) for details of the
software architecture, for building the firmware and for configuration.
