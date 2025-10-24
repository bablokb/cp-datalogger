Tools
=====

A number of tools (python scripts) are available in `tools`. They are
copied to the device and can be started from the REPL or on a computer.


show_sd.py
----------

This tool allows REPL access to CSV-files and logs (if the SD is
configured as the logger-target).

From the REPL, run:

    from tools import show_sd

and follow the instructions. Basically, you can run the following functions:

  - show_sd.dump_file(filename)
  - show_sd.del_file(filename)


scd4x_config.py
---------------

This is a configuration tool for SCD40/SCD41 sensors.

From the REPL, run:

    from tools import scd4x_config

and follow the instructions. The import configures I2C and defines the
function

    scd4x_config.run(altitude=None,persist=False,duration=10,ppm=418,temp_offset=4)

Running this function, e.g. with

    scd4x_config.run(altitude=525,persist=True,temp_offset=8)

will set the altitude and the temperature offset. The latter has to be
determined emperically (the sensor default builtin value is 4).
