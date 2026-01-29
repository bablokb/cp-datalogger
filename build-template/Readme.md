Build Template
==============

This directory contains build template files for a datalogger (`DL1`)
and for a gateway (`GW`).

For building you need a unix-like environment with at least GNU-make.
Besides Linux, MacOS works. WSL ("Windows Subsystem for Linux")
probably also works, but hasn't been tested.


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

From the toplevel directory (`pcb-pico-datalogger`) run

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

From the toplevel directory (`pcb-pico-datalogger`) run

    make gateway MAKEVARS=configs.local/GW/makevars.mk

This will create a folder `GW.local`. Copy everything **below** this
folder to the Pico of the gateway.

*Re-building*, e.g. you only changed the configuration, just needs a

    make

To cleanup the build-environment, run

    make clean
