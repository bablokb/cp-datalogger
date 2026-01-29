#-----------------------------------------------------------------------------
# Sensor definition for AM2320.
#
# Naming convention:
#   - filenames in lowercase (am2320.py)
#   - class name the same as filename in uppercase (AM2320)
#   - the constructor must take four arguments (config,i2c,addr,spi)
#     and probe for the device
#   - the read-method must update the data and return a string with the
#     values for the csv-record
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

PROPERTIES = "t h"          # properties for the display
FORMATS = {
  "t":   ["T/AM:", "{0:.1f}°C"],
  "h":   ["H/AM:", "{0:.0f}%rH"]
  }

from log_writer import Logger
g_logger = Logger()

import adafruit_am2320

class AM2320:
  headers = 'T/AM °C,H/AM %rH'

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """

    self.ignore = False
    self.am2320 = None
    for nr,bus in enumerate(i2c):
      if not bus:
        continue
      try:
        g_logger.print(f"testing am2320 on i2c{nr}")
        self.am2320 = adafruit_am2320.AM2320(bus)
        g_logger.print(f"detected am2320 on i2c{nr}")
        break
      except Exception as ex:
        g_logger.print(f"exception: {ex}")
    if not self.am2320:
      raise Exception("no am2320 detected. Check config/cabling!")

    # dynamically create formats for display...
    self.PROPERTIES = getattr(config,"AM2320_PROPERTIES",PROPERTIES).split()
    self.formats = []
    for p in self.PROPERTIES:
      self.formats.extend(FORMATS[p])

  def read(self,data,values):
    """ read sensor """
    t = round(self.am2320.temperature,1)
    h = round(self.am2320.relative_humidity,0)
    data["am2320"] = {
      "t": t,
      "h":  h,
      FORMATS['t'][0]: FORMATS['t'][1].format(t),
      FORMATS['h'][0]: FORMATS['h'][1].format(h)
    }
    if not self.ignore:
      for p in self.PROPERTIES:
        values.extend([None,data["am2320"][p]])
    return f"{t:0.1f},{h:0.0f}"
