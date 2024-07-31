#-----------------------------------------------------------------------------
# Sensor definition for MCP9808.
#
# Naming convention:
#   - filenames in lowercase (mcp9808.py)
#   - class name the same as filename in uppercase (MCP9808)
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

import adafruit_mcp9808

class MCP9808:
  formats = ["T/MCP:", "{0:.1f}°C"]
  headers = 'T/MCP °C'

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """

    self.ignore = False
    self.mcp9808 = None
    for nr,bus in enumerate(i2c):
      if not bus:
        continue
      try:
        g_logger.print(f"testing mcp9808 on (i2c{nr},{addr})")
        self.mcp9808 = adafruit_mcp9808.MCP9808(bus,0x18 if not addr else addr)
        g_logger.print(f"detected mcp9808 on i2c{nr}")
        break
      except Exception as ex:
        g_logger.print(f"exception: {ex}")
    if not self.mcp9808:
      raise Exception("no mcp9808 detected. Check config/cabling!")

  def read(self,data,values):
    t = round(self.mcp9808.temperature,1)
    data["mcp9808"] = {
      "t": t
    }
    if not self.ignore:
      values.extend([None,t])
    return  f"{t:0.1f}"
