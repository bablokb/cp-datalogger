Build Template
==============

This directory contains build template files for a datalogger (`DL1`)
and for a gateway (`GW`). Both devices should run CircuitPython 9.2.9.

The build needs a unix-like environment with at least GNU-make.
Besides Linux, MacOS is knowned to work. WSL ("Windows Subsystem for
Linux") probably also works, but hasn't been tested.


Preparation
-----------

After checkout, create a directory `configs.local` and copy the
**contents** of `build-template` to `configs.local`. *Never edit any
files from `build-template` directly*.

    git clone https://github.com/bablokb/cp-datalogger.git
    cd cp-datalogger
    mkdir configs.local
    cp -a build-template/* configs.local/


Build Configuration
-------------------

Edit the file `makevars.mk` in the folders `DL1` and `GW`. You will
have to set the correct PCB version (`PCB=v?`) and select the
log-configuration.

If you rename the folder names (or add additional folders for more
dataloggers) you must also edit the `makevars.mk` to match the
paths.


Logger and Gateway Configuration
--------------------------------

The folders `DL1` and `GW` contain example `config.py`-files for a
datalogger and for a gateway. Note that there are far more
configuration options, see the docs for a complete list. Most of them
are not necessary except for special cases.

Things you typically want to change are the identification strings,
the `SENSORS=` configuration and the LoRa-settings. Make sure that
`LORA_BASE_ADDR` for the datalogger matches `LORA_NODE_ADDR` from the
gateway. Also, the quality-of-service setting (`LORA_QOS`) must match
between logger and gateway.


Building the Datalogger
-----------------------

From the toplevel directory (`cp-datalogger`) run

    make default MAKEVARS=configs.local/DL1/makevars.mk

This will create a folder `DL1.local`. Copy everything **below** this
folder to the Pico of the datalogger.

*Re-building*, e.g. you only changed the configuration, just needs a

    make

To cleanup the build-environment, run

    make clean


Building the Gateway
--------------------

Before building the gateway, make sure to clean the build environment
as described above.

From the toplevel directory (`cp-datalogger`) run

    make gateway MAKEVARS=configs.local/GW/makevars.mk

This will create a folder `GW.local`. Copy everything **below** this
folder to the Pico of the gateway.

*Re-building*, e.g. you only changed the configuration, just needs a

    make

To cleanup the build-environment, run

    make clean


Setting Time
------------

To set the time of the datalogger and gateway, press the reset button
while holding the "A" button pressed. This will start [administration
mode](../docs/admin_mode.md). Both devices will provide a
WLAN. Connect to the devices, open a browser and set the time from the
main menu. This will sync the time of your PC, laptop or smartphone to
the device.

Afterwards, restart both devices.


Testing LoRa
------------

Make sure the antennas of both devices are vertically orientated. There
is nothing special to do with the gateway, but for testing LoRa, the
datalogger should switch to [broadcast-mode](../docs/broadcast_mode.md).

Press the reset button of the datalogger while holding the "B" button
pressed. Wait until the system comes up, then release the "B" button.

Once in broadast-mode, the datalogger will send a short message to
the gateway every minute. For LoRa, faster rates would be possible
but the e-ink display would suffer with faster updates.

The datalogger can move around while keeping the gateway fixed to test
different locations with different distances. The gateway logs all
received packages including technical data like signal-to-noise ratio
or signal-strength.

Repeat the test with different settings of `LORA_QOS` if necessary.
