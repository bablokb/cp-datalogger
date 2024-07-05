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

from log_writer import Logger
g_logger = Logger()

import adafruit_ahtx0

class AHT20:
  formats = ["T/AHT:", "{0:.1f}°C","H/AHT:", "{0:.0f}%rH"]
  headers = 'T/AHT °C,H/AHT %rH'

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """
    self.ignore = False
    self.aht20 = None
    for bus,nr in i2c:
      try:
        g_logger.print(f"testing aht20 on i2c{nr}")
        self.aht20 = adafruit_ahtx0.AHTx0(bus)
        g_logger.print(f"detected aht20 on i2c{nr}")
        break
      except Exception as ex:
        g_logger.print(f"exception: {ex}")
    if not self.aht20:
      raise Exception("no aht20 detected. Check config/cabling!")

  def read(self,data,values):
    """ read sensor """
    t = round(self.aht20.temperature,1)
    h = round(self.aht20.relative_humidity,0)
    data["aht20"] = {
      "temp": t,
      "hum":  h
    }
    if not self.ignore:
      values.extend([None,t])
      values.extend([None,h])
    return f"{t:0.1f},{h:0.0f}"
