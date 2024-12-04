Pico Datalogger with Integrated Power-Management
================================================

This is a hardware and software solution for low-frequency
data-logging with a Raspberry Pi Pico (W). The project started as a
hardware project, but the software runs independently of the special
hardware (PCBs) provided in this repository (see some example setups
as provided in the `examples` folder). Nevertheless, the full function
set of the software is not available with standard components.

Besides logging data to a SD-card, the dataloggers can send data to a
central system (called "gateway"). Normally the gateway acts as a
relay to upstream systems, but it could do anything with the data. See
[Gateway Application Firmware](docs/software_gateway.md) for details.


Core software functions
-----------------------

  * implemented in CircuitPython
  * support for an external RTC for exact time keeping
  * cyclical sensor readout for a wide range of environmental
    [sensors](docs/sensors.md) (currently 18 directly support
    including Open-Meteo weather data)
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


Core hardware functions (PCBs)
------------------------------

  * power management for extremly low standby current (about 1µA)
  * embedded XTSD-chip (emulates a micro-SD card)
  * connectors (Pico, Stemma/Qt, UART)
  * JST-PH2 connector for LiPo or battery pack (two AA/AAA)
  * a sensor PCB with a number of standard sensors
    (temperature, humidity, light, noise)

The design has gone through multiple iterations, you
can find images of these versions in the `docs` folder.

Current base PCB:

![](docs/pcb-datalogger-v2-2.jpg)

Sensor PCB:

![](docs/pcb-sensor-2.jpg)

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


Background
----------

For background on and motivation for this project, please see
<https://opendeved.net/programmes/ilce-in-tanzania/>.


Additional resources
--------------------

  * [Sensors](docs/sensors.md)
  * [Tasks](docs/tasks.md)
  * [Components](docs/components.md)
  * [Hardware Architecture](docs/hw_architecture.md)
  * [Power](docs/power.md)
  * [Pinout](docs/pins.md)
  * [Pinout V2](docs/pins-v2.md)
  * Case for this PCB: https://github.com/OpenDevEd/case-for-pico-datalogger-rev1.00
  * [KiCAD design-files V1](./pico-datalogger.kicad/Readme.md)
  * [KiCAD design-files V2](./pico-datalogger-v2.kicad/Readme.md)
  * [KiCAD design-files sensor-PCB](./pico-sensor-pcb.kicad/Readme.md)
  * [KiCAD design-files display-adapter](./display-adapter.kicad/Readme.md)
  * [KiCAD design-files LoRa-adapter](./lora-adapter.kicad/Readme.md)
  * [References](docs/references.md)


License
-------

Software in `src` is licensed under the GPL3. Hardware is licensed by:

[![CC BY-SA 4.0][cc-by-sa-shield]][cc-by-sa]

This work is licensed under a
[Creative Commons Attribution-ShareAlike 4.0 International
License][cc-by-sa].

[![CC BY-SA 4.0][cc-by-sa-image]][cc-by-sa]

[cc-by-sa]: http://creativecommons.org/licenses/by-sa/4.0/
[cc-by-sa-image]: https://licensebuttons.net/l/by-sa/4.0/88x31.png
[cc-by-sa-shield]:
https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg
