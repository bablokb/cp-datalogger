#-----------------------------------------------------------------------------
# Sensor definition for the voltage-monitor.
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

import board
from analogio import AnalogIn

class BATTERY:
  formats = ["Bat:","{0:0.2f}V"]
  headers = 'Bat V'

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """

  def read(self,data,values):
    """ read voltage monitor """

    if hasattr(board,"VOLTAGE_MONITOR"):
      adc = AnalogIn(board.VOLTAGE_MONITOR)
      level = round(adc.value *  3 * 3.3 / 65535,2)
      adc.deinit()
      if level < 1.8 or level > 5.5:
        # this happens only if the voltage-monitor is external and not connected
        # in this case, fake the level to prevent triggering level-based logic
        level = 3.5
    else:
      level = 3.5
    data["battery"] = level
    values.extend([None,level])
    return f"{level:0.2f}"
