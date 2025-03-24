Software Deployment
===================

The usual deployment process for CircuitPython just copies all files to
the CIRCUITPY-drive and that's it. For this large project, this does
not work anymore due to space constraints. The solution is to precompile
and compress all files.


Prerequisites
-------------

Deployment needs the following tools:

  - make
  - gzip
  - mpy-cross

The first two tools should be installed on any contemporary
Linux-system (or the WSL). The last tool is part of this repository in
the `bin/`-subdirectory assuming the build-system runs on a Linux
host. See
<https://adafruit-circuit-python.s3.amazonaws.com/index.html?prefix=bin/mpy-cross/>.
for other versions.

**Note: if the versions of mpy-cross provided in `bin/` are not
correct for your OS-environment, download the correct versions and put
them somewhere in your `PATH`. Be sure to name them `mpy-cross8` and
`mpy-cross9`.**


Simple Usage
------------

Run

    > make

in the root-directory of the project. This creates the subdirectory `deploy`.
After that, you can manualy copy all files below `deploy` to your device.

To select between CircuitPython 8.x and 9.x builds, pass `CP_VERSION=8|9`
to `make`. The default is `CP_VERSION=9`.


Select Datalogger-PCB version
-----------------------------

The default builds a system for the v2 version of the datalogger PCB. To
build a system for the v1 PCB, run

    > make PCB=v1

This make-variable pulls in the correct pin-mapping
(`src/pins${PCB}.py`).  For other mappings pass in a different value
for `PCB` (e.g. when using a PicoBell Adalogger: `PCB=pbada`). Create
an appropriate named pin-configuration file if necessary.

You can also pass in a path to the mapping file, in this case the mapping
file can be out of tree (i.e. not within the `src/`-direcotory).


Direct Deployment
-----------------

Run

    > make DEPLOY_TO=/path/to/your/mounted/CIRCUITPY

This will directly update files on your device if the CIRCUITPY-drive is
already mounted.


Advanced Usage
--------------

You can pass paths to your specific configurations and secrets-files on
the commandline:

    > make PCB=v1|v2|path-to-pins.py \
         DEPLOY_TO=whatever \
         CONFIG=my_special_config.py \
         LOG_CONFIG=my_logconfiguration.py \
         AP_CONFIG=my_apconfiguration.py \
         SECRETS=my_credentials.py \
         CP_VERSION=9

After invocation of make, the commandline arguments are saved and reused.
I.e. a subsequent call to make does not need the arguments anymore.


You can even keep sets of make-variables, e.g.:

    > cat my_vars.txt
      PCB=v1|v2|path-to-pins.py
      DEPLOY_TO=whatever
      CONFIG=my_special_config.py
      LOG_CONFIG=my_logconfiguration.py
      AP_CONFIG=my_apconfiguration.py
      SECRETS=my_credentials.py
      CP_VERSION=8

    > make MAKEVARS=my_vars.txt

Again, make remembers all relevant variables (in the file `makevars.tmp`)
and does not need the argument on subsequent runs.


Building the Gateway-Firmware
-----------------------------

The buildsystem also supports the gateway. While the "default" target builds
the datalogger-firmware, the target "gateway" builds the gateway software:

    make gateway MAKEVARS=...

Otherwise, the mechanisms are the same for both.


Cleanup
-------

To cleanup a temporary `deploy`-directory (and the file `makevars.tmp`),
run

    make clean

If you deployed directly to your device, this will erase your device, so
take care.
