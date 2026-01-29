#-----------------------------------------------------------------------------
# Sensor definition for HDC302x.
#
# Naming convention:
#   - filenames in lowercase (hdc302x.py)
#   - class name the same as filename in uppercase (HDC302X)
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
  "t":   ["T/HDC:", "{0:.1f}°C"],
  "h":   ["H/HDC:", "{0:.0f}%rH"]
  }

from log_writer import Logger
g_logger = Logger()

import time
import adafruit_hdc302x

class HDC302X:
  headers = 'T/HDC °C,H/HDC %rH'

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """
    self.ignore = False
    self.hdc302x = None
    address = addr if addr else 0x44
    for nr,bus in enumerate(i2c):
      if not bus:
        continue
      try:
        g_logger.print(f"testing hdc302x on (i2c{nr},{address})")
        self.hdc302x = adafruit_hdc302x.HDC302x(bus)
        g_logger.print(f"detected hdc302x on (i2c{nr},{address})")
        break
      except Exception as ex:
        g_logger.print(f"exception: {ex}")
    if not self.hdc302x:
      raise Exception("no hdc302x detected. Check config/cabling!")

    # dynamically create formats for display...
    self.PROPERTIES = getattr(config,"HDC302X_PROPERTIES",PROPERTIES).split()
    self.formats = []
    for p in self.PROPERTIES:
      self.formats.extend(FORMATS[p])

  def read(self,data,values):
    """ read sensor """
    while True:
      t = round(self.hdc302x.temperature,1)
      h = round(self.hdc302x.relative_humidity,0)
      # the very first measurement after power up seems to be invalid
      if t > -45:
        break
      else:
        time.sleep(0.05)
    data["hdc302x"] = {
      "t": t,
      "h":  h,
      FORMATS['t'][0]: FORMATS['t'][1].format(t),
      FORMATS['h'][0]: FORMATS['h'][1].format(h)
    }
    if not self.ignore:
      for p in self.PROPERTIES:
        values.extend([None,data["hdc302x"][p]])
    return f"{t:0.1f},{h:0.0f}"
