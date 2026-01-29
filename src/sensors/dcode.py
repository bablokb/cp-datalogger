#-----------------------------------------------------------------------------
# Sensor definition for data-coding (pseudo-sensor)
#
# This "sensor" returns a code that describes the sensor-data. The use-case
# is a central data-hub that receives data from various loggers. With the
# dcode, each line is well-defined even if the sensors for a given
# LOGGER_ID change.
#
# Example:
#   SENSORS="id dcode battery aht20 bh1750 pdm"
#   -> dcode="01235D"
#   -> sample-csv-record: "001,01235D,2.75,23.3,44,200,143"
#
# Note: new sensors must be added to the mapping in this file.
#
# Naming convention:
#   - filenames in lowercase (dcode.py)
#   - class name the same as filename in uppercase (DCODE)
#   - the constructor must take four arguments (config,i2c,addr,spi)
#     and probe for the device
#   - the read-method must update the data and return a string with the
#     values for the csv-record
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

from sensor_meta import SENSOR_MAP

class DCODE:
  formats = []             # empty: don't show on display
  headers = 'DCODE'

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """

    # map all defined sensors (the first column (timestamp) is not encoded)
    self._dcode = ""
    for sensor in config.SENSORS.split(' '):
      sensor = sensor.split('(')[0]         # remove optional parameters
      self._dcode = f"{self._dcode}{SENSOR_MAP[sensor]}"

  def read(self,data,values):
    """ 'read' dcode """

    data["dcode"] = self._dcode
    return self._dcode
