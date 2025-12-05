Upgrading the CircuitPython Firmware
====================================

Standard Procedure
------------------

Entering the firmware update mode works by keeping the boot-button
of the Pico pressed while plugging in the Pico to the host computer.
As an alternative, if CircuitPython is already installed, double click
the reset button - this might need some retries to get the speed of
the double-click right.

After the Pico is in firmware update mode, you should have a new drive
(Windows) or device (Linux) with 128 MB. Follow the normal procedure
on how to [update
CircuitPython](https://learn.adafruit.com/welcome-to-circuitpython/installing-circuitpython).

If the standard procedure does not work, e.g. because the boot-button
is not exposed (i.e. within an enclosure) and the double-click trick
does not work, use the method in the next section.


Procedure for Assembled Dataloggers
-----------------------------------

Assembled dataloggers don't expose the boot-button. To enter firmware
upgrade mode, use the following steps:

If the device is still running CircuitPython 8.0.5:

  - switch to the branch 8.0.5 of the datalogger repository
    (`git switch 8.0.5`)
  - build and deploy the newest version of the datalogger software. This
    version is still for 8.0.5-systems.
  - update the datalogger software on the device

When done:

  - **restart the device while keeping button C pressed**
  - the device will boot into (C=CircuitPython) firmware update mode
  - once in firmware update mode, follow the standard procedure to
    update the firmware
  - switch back to the main branch of the datalogger repository
    (git switch main)
  - build and deploy the newest version of the datalogger software. This
    is now the version for 9.2.x-systems.
  - update the datalogger software on the device
  - you should now have both a 9.2.x CircuitPython firmware and the
    application code compiled for 9.2.x
