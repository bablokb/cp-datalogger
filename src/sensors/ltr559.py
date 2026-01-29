#-----------------------------------------------------------------------------
# Sensor definition for LTR559.
#
# Naming convention:
#   - filenames in lowercase (ltr559.py)
#   - class name the same as filename in uppercase (LTR559)
#   - the constructor must take four arguments (config,i2c,addr,spi)
#     and probe for the device
#   - the read-method must update the data and return a string with the
#     values for the csv-record
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

from log_writer import Logger
g_logger = Logger()

from pimoroni_circuitpython_ltr559 import Pimoroni_LTR559

class LTR559:
  formats = ["L/LTR:", "{0:.0f}lx"]
  headers = 'L/LTR lx'

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """

    self.ignore = False
    self.ltr559 = None
    for nr,bus in enumerate(i2c):
      if not bus:
        continue
      try:
        g_logger.print(f"testing ltr559 on i2c{nr}")
        self.ltr559 = Pimoroni_LTR559(bus)
        g_logger.print(f"detected ltr559 on i2c{nr}")
        break
      except Exception as ex:
        g_logger.print(f"exception: {ex}")
    if not self.ltr559:
      raise Exception("no ltr559 detected. Check config/cabling!")

  def read(self,data,values):
    lux = round(self.ltr559.lux,0)
    data["ltr559"] = {
      "l": lux,
      self.formats[0]: self.formats[1].format(lux)
    }
    if not self.ignore:
      values.extend([None,lux])
    return f"{lux:.0f}"
