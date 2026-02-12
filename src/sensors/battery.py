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
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

import board
from analogio import AnalogIn
import time

import pins

class BATTERY:
  formats = ["Bat:","{0:0.2f}V"]
  headers = 'Bat V'

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """
    self.ignore = False
    self._samples = getattr(config,"BATTERY_SAMPLES",1)

  def read(self,data,values):
    """ read voltage monitor """

    if hasattr(pins,"PIN_VOLTAGE_MONITOR"):
      adc = AnalogIn(pins.PIN_VOLTAGE_MONITOR)
      level = adc.value
      for _ in range(1,self._samples):
        time.sleep(0.01)
        level += adc.value
      adc.deinit()
      level = round(level/self._samples*9.9/65535,2)  # 3*3.3 = 9.9
      if level < 1.8 or level > 5.5:
        # this happens only if the voltage-monitor is external and floating
        # in this case, fake the level to prevent triggering level-based logic
        level = 3.5
    else:
      level = 3.5
    data["battery"] = level
    if not self.ignore:
      values.extend([None,level])
    return f"{level:0.2f}"
