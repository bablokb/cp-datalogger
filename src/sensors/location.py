#-----------------------------------------------------------------------------
# Sensor definition for the LOGGER_LOCATION (pseudo-sensor)
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

class LOCATION:
  formats = []             # empty: don't show on display
  headers = 'LOCATION'

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """
    self._config = config

  def read(self,data,values):
    """ 'read' location """

    data["location"] = self._config.LOGGER_LOCATION
    return f"{self._config.LOGGER_LOCATION}"
