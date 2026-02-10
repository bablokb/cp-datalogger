Pico Datalogger with Integrated Power-Management
================================================

This is a hardware and software solution for low-frequency
data-logging with a Raspberry Pi Pico (W). The project started as a
hardware project, but the software runs independently of the special
hardware (PCBs) created. Nevertheless, the full function
set of the software is not available with standard components.

Besides logging data to a SD-card, the dataloggers can send data to a
central system (called "gateway"). Normally the gateway acts as a
relay to upstream systems, but it could do anything with the data. See
[Gateway](docs/gateway.md) for details.

This repository only contains the software for the datalogger/gateway.
For links to custom made PCBs, see below.


Core software functions
-----------------------

  * implemented in CircuitPython
  * support for an external RTC for exact time keeping
  * cyclical sensor readout for a wide range of mostly environmental
    [sensors](docs/sensors.md) (currently 25 directly support
    including Open-Meteo weather data and Tasmota power monitoring)
  * supports I2C (two busses), UART-3V3 and UART-5V devices
  * support I2C-multiplexers (PCA954xA, TCA954xA)
  * readout in intervals or using a time-table
  * implementation of additional sensors only need a small wrapper class
    (given a driver-library is available)
  * logging of data to a micro-SD card or equivalent (e.g. XTSD-chip)
  * configurable post-collection [tasks](docs/tasks.md)
    (e.g. update of a display, sending data using WLAN or LoRa)
  * send data to a gateway (see below)
  * power-optimized programs
  * [web-interface](docs/admin_mode.md) for configuration and data download
  * no programming required for standard setups
  * supports (almost) zero current sleep with specialized hardware


For installation and operation, read the documents linked in the next
section.


Quick Links
-----------

  * [Hardware Setup](docs/hardware.md)
  * [Software (Datalogger)](docs/software_datalogger.md)
  * [Software (Gateway)](docs/software_gateway.md)
  * [Configuration](docs/configuration.md)
  * [Software deployment](docs/deployment.md)
  * [Examples](examples/README.md)
  * [Initial setup of the RTC](docs/rtc_setup.md)
  * [Tools and Scripts](docs/tools.md)
  * [Administration mode](docs/admin_mode.md)
  * [Broadcast mode](docs/broadcast_mode.md)
  * [Setup of Blues-Gateway](docs/blues-gateway.md)


Additional resources
--------------------

  * [Sensors](docs/sensors.md)
  * [Tasks](docs/tasks.md)
  * [Components](docs/components.md)
  * [Hardware Architecture](docs/hw_architecture.md)
  * [Power](docs/power.md)
  * [Pinout](docs/pins.md)
  * [Pinout V2](docs/pins-v2.md)
  * [Pinout V3](docs/pins-v3.md)


PCBs
----

  * <https://github.com/bablokb//pcb-datalogger-v3>:
    Pico board for data-logging with power-management and XTSD storage
  * <https://github.com/bablokb//pcb-datalogger-v2>:
    Pico board for data-logging with power-management and XTSD storage
  * <https://github.com/bablokb//pcb-datalogger-sensor-pcb>:
    Sensor PCB for the Pico Datalogger-v2
  * <https://github.com/bablokb//pcb-datalogger-display-adapter>:
    Display-Adapter PCB
  * <https://github.com/bablokb//pcb-datalogger-lora-adapter>:
    LoRa-Adapter PCB (adds SUR-Connector to Adafruit-Breakout)
  * <https://github.com/bablokb//pcb-datalogger-lora-pcb>:
    A PCB with a LoRa tranceiver and a SUR Connector
  * <https://github.com/bablokb//pcb-datalogger-v1>:
    Pico board for data-logging with power-management and XTSD storage
  * <https://github.com/bablokb//pcb-surs-cable-tester>:
    A small PCB to test the type of a 8-pin SUR cable


3D-Files
--------

  * <https://github.com/bablokb//3D-datalogger-v3-case>:
    Design Files for a Case for the Pico-Datalogger-v3
  * <https://github.com/bablokb//3D-datalogger-v2-case>:
    Design Files for a Case for the Pico-Datalogger-v2
  * <https://github.com/bablokb//3D-datalogger-stevenson>:
    Ddesign Ffiles (supports, OpenSCAD) for a Stevenson Screen Enclosure
  * <https://github.com/bablokb//3D-datalogger-v1-case>:
    Design Files for a Case for the Pico-Datalogger-v1
  * <https://github.com/OpenDevEd/case-for-pico-datalogger-rev1.00>:
    Design Files for an alternative case for the Pico-Datalogger-v1


Background
----------

For background on and motivation for this project, please see
<https://opendeved.net/programmes/ilce-in-tanzania/>.


License
-------

Software in `src` is licensed under the GPL3.
