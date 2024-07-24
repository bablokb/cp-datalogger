Admin-Mode
==========

Overview
--------

Administration mode supports the following tasks:

  - download and update of the base configuration file `config.py`
  - download and delete of the logfile (if logging to sd-card is enabled)
  - download and delete of csv-files with sensor-measurements
  - set the time of the device

To enter the administration mode, use the steps outlined below. Leaving
the administration mode needs a hard reset using the reset-button.


Configuration
-------------

Various aspects of the admin-mode can be configured. The optional
file `ap_config.py` can be used to override settings. See
[AP configuration](./ap_config.md) for details.


Start Admin-Mode
----------------

Administration mode can only be entered during start or reset. When the
device is powered down, keep holding SW-A and shortly press the on-button.
If running (e.g. in continuous mode), keep holding SW-A and shortly press
the reset-button.

Keep pressing the SW-A button until admin-mode is up and running. In
this state, you can see the state on the display. On a v2-system with
sensor-PCB, the red-LED is full on.

For the v1 datalogger-PCB, the SW-A button is available from the display.
For the v2-PCB, the SW-A button is on the sensor-PCB.


Using the Admin-Mode
--------------------

Admin-mode creates a dedicated WLAN-network with the SSID as
configured in `ap_config.py` (defaults to `datalogger`). Connect your
browser to the IP of the access-point (usually `192.168.4.1`).

The interface is responsive and should be simple to use from desktop
or mobile systems.

Critical functions (i.e. upload of a new `config.py` or the manual
configuration of `config.py`) is disabled on low battery.


Stop Admin-Mode
---------------

Admin-mode must be stopped with a hard-reset, e.g. a power-cycle or
pressing the reset button.


Current draw
------------

Note that admin-mode drains the battery fast and therefore should not
be kept running on batteries longer than necessary.
