Setup
=====

Overview
--------

In this repo you will find various KiCAD design files for the base
and sensor PCB as well as various adapters. All of this is optional, the
software will run on other hardware as well, but with limited
functionality. In the directory `production_files` you will find ready
to order production files for JCLPCB. You typically need the gerber
zipfile, a BOM (bill of materials) and a CPL (pick and place) file.

A number of components are optional. E.g. the SURS-connectors are not
strictly necessary, because you also have througholes as an alternative.
In addition you can save money if you solder the JST-connectors
yourself.


Generic Hardware
----------------

The simplest hardware-setup would be a standalone Pico-W. The device
could read it's builtin sensors or data from the internet. More
realistically, you would add some I2C-sensors, a SD-card breakout for
data-storage and a RTC (currently the PCF8523, PCF8563 and PCF85063(A)
are supported). As a quick-start, the Adafruit PiCowbell Datalogger
(<https://www.adafruit.com/product/5703>) will provide the SD-card
slot and the RTC.

For low-power operation, add a TPL5110 (<https://www.adafruit.com/product/3435>)
or a TPL5111 (<https://www.adafruit.com/product/3573>). The first one
drives power (i.e. connect to VSYS of the Pico), the second one
drives the enable pin (e.g. connect to EN). Both solutions support
sampling intervals up to two hours, but no time-table operation.

You can find some example setups with generic hardware in the
[examples](../examples/README.md) directory.

Additional steps:

  - create a file `pins<name>.py` with the correct pin-mapping. Use one
    of the existing files `src/pins*.py` as a template.
    You don't have to support (connect) all pins if you don't plan to
    use the specific hardware (e.g. LoRa).
  - Connect other hardware components as needed (power, sensors and so on).


Datalogger-PCBs
---------------

The specialized datalogger PCBs support a number of important functions:

  * power management for extremly low standby current (about 1µA)
  * embedded XTSD-chip (emulates a micro-SD card)
  * connectors (Pico, Stemma/Qt, UART)
  * JST-PH2 connector for LiPo or battery pack (two AA/AAA)
  * a sensor PCB with a number of standard sensors
    (temperature, humidity, light, noise)

The design has gone through multiple iterations, you can find images
of these versions in the `docs` folder.

Current base PCB:

![](docs/pcb-datalogger-v2-2.jpg)


Sensor PCB
----------

The sensor PCB provides a number of standard sensors (AHT20, BH1750
and PDM-microphone), five buttons and one application LED.

![](docs/pcb-sensor-2.jpg)

The buttons support the following functions:

  - ON: start the datalogger (e.g. for an on-demand measurement)
  - RST: restart the datalogger
  - A: hold during boot to start in [Administration mode](./admin_mode.md)
  - B: hold during boot to start in [broadcast mode](./broadcast_mode.md)
  - C: hold during boot to start in firmware update mode


Setup Datalogger-PCBs
---------------------

To setup the PCBs of this repo:

  - Connect a battery pack (two AAA/AA batteries or a single cell LiPo)
    via the battery port
  - Add a coin cell to maintain data on the RTC (CR2032)
  - Plug in a Pico (W)
  - Add sensors to the appropriate connectors
  - v1: Always remove the jumper if you plugin the USB-cable to the Pico, e.g.
    for software updates.
  - v1: (optional) Plug in the display (Pimoroni Inky-Pack) from behind.
  - v2: connect the sensor PCB, the display (optional) and LoRa adapter
    (optional) via SURS-cables.


Software
--------

Head on to

  - [Software (Datalogger)](./software_datalogger.md)
  - [Software (Gateway)](./software_gateway.md)
