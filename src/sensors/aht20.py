#-----------------------------------------------------------------------------
# Sensor definition for AHT20.
#
# Naming convention:
#   - filenames in lowercase (aht20.py)
#   - class name the same as filename in uppercase (AHT20)
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
  "t":   ["T/AHT:", "{0:.1f}°C"],
  "h":   ["H/AHT:", "{0:.0f}%rH"]
  }

from log_writer import Logger
g_logger = Logger()

import adafruit_ahtx0

class AHT20:
  headers = 'T/AHT °C,H/AHT %rH'

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """
    self.ignore = False
    self.aht20 = None
    for nr,bus in enumerate(i2c):
      if not bus:
        continue
      try:
        g_logger.print(f"testing aht20 on i2c{nr}")
        self.aht20 = adafruit_ahtx0.AHTx0(bus)
        g_logger.print(f"detected aht20 on i2c{nr}")
        break
      except Exception as ex:
        g_logger.print(f"exception: {ex}")
    if not self.aht20:
      raise Exception("no aht20 detected. Check config/cabling!")

    # dynamically create formats for display...
    self.PROPERTIES = getattr(config,"AHT20_PROPERTIES",PROPERTIES).split()
    self.formats = []
    for p in self.PROPERTIES:
      self.formats.extend(FORMATS[p])

  def read(self,data,values):
    """ read sensor """
    t = round(self.aht20.temperature,1)
    h = round(self.aht20.relative_humidity,0)
    data["aht20"] = {
      "t": t,
      "h":  h,
      FORMATS['t'][0]: FORMATS['t'][1].format(t),
      FORMATS['h'][0]: FORMATS['h'][1].format(h)
    }
    if not self.ignore:
      for p in self.PROPERTIES:
        values.extend([None,data["aht20"][p]])
    return f"{t:0.1f},{h:0.0f}"
