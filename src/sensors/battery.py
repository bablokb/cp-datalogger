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
#from log_writer import Logger
#g_logger = Logger()

class BATTERY:
  formats = ["Bat:","{0:0.2f}V"]
  headers = 'Bat V'

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """
    self.ignore = False
    self._config = config

  def _trimmed_value(self, adc):
    """ return multi-sampled and trimmed value """

    samples = max(getattr(self._config,"BATTERY_SAMPLES",5),3)
    l_min = adc.value
    l_max = l_min
    l_sum = l_min
    #g_logger.print(f"battery: level(0) = {self._scaled_value(l_min)}")
    for i in range(1,samples):
      time.sleep(0.01)
      level = adc.value
      #g_logger.print(f"battery: level({i}) = {self._scaled_value(level)}")
      l_sum += level
      if level<l_min:
        l_min = level
      elif level>l_max:
        l_max = level
    # remove lowest and highest reading and return mean
    return (l_sum-l_min-l_max)/(samples-2)

  def _scaled_value(self,value):
    """ return scaled value """
    return round(value*9.9/65535,2)  # 3*3.3 = 9.9

  def read(self,data,values):
    """ read voltage monitor """

    if hasattr(pins,"PIN_VOLTAGE_MONITOR"):
      adc = AnalogIn(pins.PIN_VOLTAGE_MONITOR)
      if getattr(self._config,"BATTERY_FILTERING",False):
        level = self._trimmed_value(adc)
      else:
        level = adc.value
      adc.deinit()
      level = self._scaled_value(level)
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
