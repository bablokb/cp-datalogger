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

The first two tools should be installed on any contemporary Linux-system
(or the WSL). The last tool can be downloaded from
<https://adafruit-circuit-python.s3.amazonaws.com/index.html?prefix=bin/mpy-cross/>.
After download, copy it to a directory in your path.


Simple Usage
------------

Run

    > make

in the root-directory of the project. This creates the subdirectory `deploy`.
After that, you can manualy copy all files below `deploy` to your device.


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

    > make PCB=v1|v2 \
         DEPLOY_TO=whatever \
         CONFIG=my_special_config.py \
         LOG_CONFIG=my_logconfiguration.py \
         AP_CONFIG=my_apconfiguration.py \
         SECRETS=my_credentials.py

After invocation of make, the commandline arguments are saved and reused.
I.e. a subsequent call to make does not need the arguments anymore.


You can even keep sets of make-variables, e.g.:

    > cat my_vars.txt
      PCB=v1|v2
      DEPLOY_TO=whatever
      CONFIG=my_special_config.py
      LOG_CONFIG=my_logconfiguration.py
      AP_CONFIG=my_apconfiguration.py
      SECRETS=my_credentials.py

    > make MAKEVARS=my_vars.txt

Again, make remembers all relevant variables (in the file `makevars.tmp`)
and does not need the argument on subsequent runs.


Cleanup
-------

To cleanup a temporary `deploy`-directory (and the file `makevars.tmp`),
run

    make clean

If you deployed directly to your device, this will erase your device, so
take care.
