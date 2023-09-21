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

from log_writer import Logger
g_logger = Logger()

import adafruit_htu31d

class HTU31D:
  formats = ["T/HTU:", "{0:.1f}°C","H/HTU:", "{0:.0f}%rH"]
  headers = 'T/HTU °C,H/HTU %rH'

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """
    self.htu31d = None
    for bus,nr in i2c:
      try:
        g_logger.print(f"testing htu31d on i2c{nr}")
        self.htu31d = adafruit_htu31d.HTU31D(bus)
        g_logger.print(f"detected htu31d on i2c{nr}")
        break
      except Exception as ex:
        g_logger.print(f"exception: {ex}")
    if not self.htu31d:
      raise Exception("no htu31d detected. Check config/cabling!")

  def read(self,data,values):
    """ read sensor """
    t,h = self.htu31d.measurements
    data["htu31d"] = {
      "temp": t,
      "hum":  h
    }
    values.extend([None,t])
    values.extend([None,h])
    return f"{t:0.1f},{h:0.0f}"
