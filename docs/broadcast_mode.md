Broadcast Mode
==============

Overview
--------

Broadcast mode supports the initial deployment of a datalogger. This
mode sends messages to the gateway using LoRa. The gateway echos these
messages with added information regarding the signal strength, thus
enabling an optimized orientation of the datalogger and it's antenna.


Prerequisites
-------------

Broadcast mode needs at least the gateway to be up and running.

To fully utilize the broadcast-mode, you should

  - plug in an OLED-display (SSD1306 128x64 or 128x32) into one
    of the free I2C-ports
  - add `HAVE_OLED=xxx` to `config.py` (see task "update_oled" in
[task-configuration](./core_config_tasks.md for details).



Starting Broadcast Mode
-----------------------

Broadcast mode can only be entered during start or reset. When the
device is powered down, keep holding SW-B and shortly press the on-button.
If running , keep holding SW-B and shortly press the reset-button.

Keep pressing the SW-B button until broadcast-mode is up and running. In
this state, you can see the state on the OLED-display. On a v2-system with
sensor-PCB, the red-LED is full on.

For the v1 datalogger-PCB, the SW-B button is available from the display.
For the v2-PCB, the SW-B button is on the sensor-PCB.


Using Broadcast Mode
--------------------

When in broadcast mode, the program queries the current time from the
gateway and updates the time on the device. After the time is updated,
the program switches to a send-receive scheme within a loop.

With an OLED-display, a new test-packet is sent every 10 seconds (this
is customizable with `BROADCAST_INT=xxx` in `config.py`). Without the
OLED, the interval is at least 60 seconds to protect the e-ink display.

On the display, the following information is available:

  - LoRa-node and Logger-ID
  - SNR (signal to noise ratio) and RSSI
    (Received Signal Strength Indication)
  - count of successful packets vs. total packets
  - RTT (round trip time - only available on the 128x64 OLED)
  - current time (only available on the 128x64 OLED)

Now the location and antenna can be optimized for maximal signal strength.

The range of RSSI is from `-120dBm` (weak) to `-30dBm` (strong). SNR
values are between `-20dB` to `+10dB`.

Absolute values are not really relevant. More important is a reliable
send-receive roundtrip as indicated by the count-number.


Stopping Broadcast Mode
-----------------------

To stop the broadcast mode, remove the OLED-display and press the reset
button. In addition to prevent excessive current draw, the system will
automatically trigger a reset after a maximum duration of xxx minutes (TBD).


Current draw
------------

Note that broadcast-mode drains the battery fast and therefore should not
be kept running on batteries longer than necessary.
