Application-Firmware
====================


Overview
--------

The application firmware of the datalogger is implemented in CircuitPython.
The sources are in the subdirectory `src` and below.

The program is a framework with these main blocks:

  - setup of the base hardware (including RTC, display, sd-card)
  - configuration of the sensors
  - data-collection
  - execution of post-collection *tasks* (e.g. save to sd, update display)
  - configuration of next wake-up alarm
  - signal shutdown to the power management circuit

The typical run-mode of the datalogger is called "strobe-mode": 

  - the power management of the datalogger-pcb turns the Pico on
  - the application firmware runs
  - power is turned off again

This mode is energy efficient and allows the operation on a pair of
AA batteries for month.


Architecture
------------

Besides the basic setup of the hardware, the program runs in two phases:

  - collect data from every configured sensor
  - execution of post-collection tasks

The configuration file `config.py` will drive these phases. See
[configuration](./configuration.md) for details on configuration.

Every sensor needs a simple wrapper that interfaces to the respective
driver-library, reads the values and updates the data. Adding new
sensors is simple, just add a python-file for the sensor in the directory
`src/sensors`. One of the existing files can be used as a blueprint.

Tasks are similar. Every task needs a wrapper in `src/tasks`.


Installation
------------

First step is to install CircuitPython on the board. Be sure to select
the version 8.0.5 (note that this is not the most current version!).

Sources:

  - If you have a Pico, install  
    <https://circuitpython.org/board/raspberry_pi_pico/>
  - If you have a Pico W, install  
    <https://circuitpython.org/board/raspberry_pi_pico_w/>

After installation of CP and a power-cycle, mount the device if not done
automatically by your operating system. Then follow the instructions
within [Software deployment](./deployment.md).


Updates
-------

The datalogger program will usually run only for a very short time. This
makes updates difficult. To enter update mode, the recommended actions are:

  - on a v1-pcb with attached batteries: remove the jumper
  - connect the device to your computer
  - if the device does not start automatically, turn it on
    using the "on"-button
  - wait a few seconds
  - hit CTRL-C

If you are connected with a serial console (e.g. from Thonny) the system
should now enter the REPL.


Next Reading
------------

  - [Configuration](./configuration.md)
  - [Initial setup of the RTC](./rtc_setup.md) 
  - [Administration mode](./admin_mode.md)
