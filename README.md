Pico Datalogger with Integrated Power-Management
================================================

This is a breakout supporting low-frequency data-logging with
a Raspberry Pi Pico. 

Core functions:
  * log data to a XTSD-chip (emulates a micro-SD card)
  * software-controlled power-control with very low standby current
  * manual or interval-based wakeup (supporting a weekly time-table)
  * supports running from a LiPo or two AA/AAA batteries 

The design has gone through multiple iterations, you
can find images of these versions in the `docs` folder.

Current PCB:

![](docs/pcb-datalogger-v2-2.jpg)

As a supplemental board we also have a sensor PCB with sensors for
temperature/humidity (AHT20), light (BH1750) and noise (PDM-mic):

![](docs/pcb-sensor-2.jpg)


Quick Links
-----------

  * [Basic Setup](docs/setup.md)
  * [Software](docs/software.md)
  * [Software deployment](docs/deployment.md)
  * [Configuration](docs/configuration.md)
  * [Initial setup of the RTC](docs/rtc_setup.md)
  * [Administration mode](docs/admin_mode.md)
  * [Broadcast mode](docs/broadcast_mode.md)
  * [Setup of Blues-Gateway](docs/blues-gateway.md)


Background
----------

For background on / motivation for this project, please see
<https://opendeved.net/programmes/ilce-in-tanzania/>.


Additional resources
--------------------

  * [Sensors](docs/sensors.md)
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
