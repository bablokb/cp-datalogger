#-----------------------------------------------------------------------------
# Sensor definition for SHT45.
#
# Naming convention:
#   - filenames in lowercase (sht45.py)
#   - class name the same as filename in uppercase (SHT45)
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

import adafruit_sht4x

class SHT45:
  formats = ["T/SHT:", "{0:.1f}°C","H/SHT:", "{0:.0f}%rH"]
  headers = 'T/SHT °C,H/SHT %rH'

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """

    self.ignore = False
    self.sht45 = None
    for bus,nr in i2c:
      try:
        g_logger.print(f"testing sht45 on i2c{nr}")
        self.sht45 = adafruit_sht4x.SHT4x(bus)
        g_logger.print(f"detected sht45 on i2c{nr}")
        break
      except Exception as ex:
        g_logger.print(f"exception: {ex}")
    if not self.sht45:
      raise Exception("no sht45 detected. Check config/cabling!")

  def read(self,data,values):
    """ read sensor """
    t = round(self.sht45.temperature,1)
    h = round(self.sht45.relative_humidity,0)
    data["sht45"] = {
      "temp": t,
      "hum":  h
    }
    if not self.ignore:
      values.extend([None,t])
      values.extend([None,h])
    return f"{t:0.1f},{h:0.0f}"
