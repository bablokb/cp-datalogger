Initial RTC-Setup
=================

Exact timestamps are important for datalogging. After startup, the
internal time (RTC) of the device is usually not valid. This is
checked by an heuristic algorithm. If the time seems invalid, the
program updates the time from the following sources if necessary:

  - external RTC (if available)
  - internet
  - (optional) saved wake up timestamp from the SD-card

Since updating the time from the internet is costly in terms of runtime
and current-draw (if possible at all), the external RTC should usually
be the source of the current time.

For the datalogger PCBs, the external RTC is powered by the battery/LiPo,
so after shutdown of the MCU this RTC keeps a valid time. In addition,
there is a backup battery (coin-cell) that should even keep the time if
the battery fails (but see below).

Nevertheless, the time of the external RTC has to be set once to a correct
value. There are a few options for this task.


Net-Update
----------

This needs access to a WLAN with correct [credentials](./secrets.md) and
the configuration of `NET_UPDATE = TRUE`. With this setup, the program
will update the external and internal RTCs automatically at startup. As
long as the external RTC is powered, this will be a one time task. So this
could be done before initial deployment in a suitable location with WLAN.


Thonny
------

Connecting to the MCU with Thonny usually sets the internal RTC to a
correct value. After startup, if the internal RTC-time is valid, this
time is propagated to the external RTC.


Administration Mode
-------------------

The time can be set manually using the [administration mode](admin_mode.md).
The main menu of the admin webpage offers an option to set the device
time to the browser time.


Broadcast Mode
--------------

Starting the device in [broadcast mode](./broadcast_mode.md) will set the
RTCs of the device from the time of the LoRa gateway.
