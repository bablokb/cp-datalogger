#-----------------------------------------------------------------------------
# Sensor definition for HTU31D.
#
# Naming convention:
#   - filenames in lowercase (htu31d.py)
#   - class name the same as filename in uppercase (HTU31D)
#   - the constructor must take four arguments (config,i2c,addr,spi)
#     and probe for the device
#   - the read-method must update the data and return a string with the
#     values for the csv-record
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

PROPERTIES = "t h"          # properties for the display
FORMATS = {
  "t":   ["T/HTU:", "{0:.1f}°C"],
  "h":   ["H/HTU:", "{0:.0f}%rH"]
  }

from log_writer import Logger
g_logger = Logger()

import adafruit_htu31d

class HTU31D:
  headers = 'T/HTU °C,H/HTU %rH'

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """
    self.ignore = False
    self.htu31d = None
    for nr,bus in enumerate(i2c):
      if not bus:
        continue
      try:
        g_logger.print(f"testing htu31d on i2c{nr}")
        self.htu31d = adafruit_htu31d.HTU31D(bus)
        g_logger.print(f"detected htu31d on i2c{nr}")
        break
      except Exception as ex:
        g_logger.print(f"exception: {ex}")
    if not self.htu31d:
      raise Exception("no htu31d detected. Check config/cabling!")

    # dynamically create formats for display...
    self.PROPERTIES = getattr(config,"HTU31D_PROPERTIES",PROPERTIES).split()
    self.formats = []
    for p in self.PROPERTIES:
      self.formats.extend(FORMATS[p])

  def read(self,data,values):
    """ read sensor """
    t,h = self.htu31d.measurements
    t = round(t,1)
    h = round(h,0)
    data["htu31d"] = {
      "t": t,
      "h":  h,
      FORMATS['t'][0]: FORMATS['t'][1].format(t),
      FORMATS['h'][0]: FORMATS['h'][1].format(h)
    }
    if not self.ignore:
      for p in self.PROPERTIES:
        values.extend([None,data["htu31d"][p]])
    return f"{t:0.1f},{h:0.0f}"
