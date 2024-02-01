Admin-Mode
==========

Overview
--------

Administration mode supports the following tasks:

  - download and update the base configuration file `config.py`
  - download and delete the logfile (if logging to sd-card is enabled)
  - download and delete of csv-files with sensor-measurements
  - set the time of the device

To enter the administration mode, use the steps outlined below. Leaving
the administration mode needs a hard reset using the reset-button.


Configuration
-------------

Various aspects of the admin-mode can be configured. The optional
file `ap_config.py` can be used to override settings.

The file needs the following content:

    from wifi import AuthMode
    ap_config = {
      'debug': False,
      'cache': True,
      'ssid': 'datalogger',
      'password': '12345678',                      # ignored for wifi.AuthMode.OPEN
      'auth_modes': [AuthMode.WPA2, AuthMode.PSK], # [wifi.AuthMode.OPEN]
      'hostname': 'datalogger'                     # msdn hostname
    }

Changing `debug` to `True` and `cache` to `False` is only needed during
development. The current version of CircuitPython does not support
AP-mode in open-mode, i.e. you need to set a password of at least 8 chars.


Start Admin-Mode
----------------

Administration mode can only be entered during start or reset. When the
device is powered down, keep holding SW-A and shortly press the on-button.
If running (e.g. in continuous mode), keep holding SW-A and shortly press
the reset-button.

Keep pressing the SW-A button until admin-mode is up and running. In
this state, you can see the state on the display. On a v2-system with
sensor-pcb, the red-LED is full on.

For the v1 datalogger-pcb, the SW-A button is available from the display.
For the v2-pcb, the SW-A button is on the sensor-pcb.


Using the Admin-Mode
--------------------

Admin-mode creates a dedicated WLAN-network with the SSID as
configured in `ap_config.py` (defaults to `datalogger`). Connect your
browser to the IP of the access-point (usually `192.168.4.1`).

The interface is responsive and should be simple to use from desktop
or mobile systems.


Stop Admin-Mode
---------------

Admin-mode must be stopped with a hard-reset, e.g. a power-cycle or
pressing the reset button.


Current draw
------------

Note that admin-mode drains the battery fast and therefore should not
be kept running on batteries longer than necessary.
