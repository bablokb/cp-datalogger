Application-Firmware
====================


Overview
--------

The application firmware of the gateway is implemented in CircuitPython.
The sources are in the subdirectory `src.gateway` and below.

The program is a framework with these main blocks:

  - core gateway services
  - receiver: a component waiting for data-transmissions from the dataloggers
  - sender: a component sending data upstream

The gateway uses the same [build system](./deployment.md) as the core
datalogger (using targets `gateway` and `copy2gateway`).

Configuration of the gateway is detailed in [Gateway
Configuration](./gatway_config.md.).


Architecture
------------

The core gateway service performs the following steps:

  - reads the configuration
  - create the receiver and sender components
  - initializes the hardware (RTC, SD, OLED if configured)
  - triggers setup for the receiver and sender
  - runs during the "active window" waiting for incoming data

The core polls the receiver for new data, passes the data on to the
sender and (optionally) saves the data to SD and updates an OLED-display.


Receivers
---------

Currently implemented receivers:

  - `LoraReceiver` (in `src.gateway/gw_rx_lora.py`)

Planned receivers:

  - `UdpReceiver`
  - `BleReceiver`
  - `HttpReceiver`


Senders
-------

Currently implemented senders:

  - `NoopSender` (in `src.gateway/gw_tx_noop.py`)  
    Does nothing, can be used as a template or for local operation, i.e.
    if the core services are sufficient for operation
  - `BluesSender` (in `src.gateway/gw_tx_blues.py`)  
    Sends data to Blues.io via a Blues-notecard

Planned senders:

  - `UdpSender`
  - `BleSender`
  - `HttpSender`
  - `MqttSender`

