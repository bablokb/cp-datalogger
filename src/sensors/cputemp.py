#-----------------------------------------------------------------------------
# Sensor definition for the cpu-temperature (pseudo-sensor).
# Mainly useful for testing.
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

import microcontroller

class CPUTEMP:
  formats = ["T/CPU:", "{0:.1f}°C"]
  headers = 'CPU temp °C'

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """
    self._config = config
    self.ignore  = False

  def read(self,data,values):
    """ read cputemp """

    temp = round(microcontroller.cpu.temperature,1)
    data["cputemp"] = temp
    if not self.ignore:
      values.extend([None,temp])
    return f"{temp}"
