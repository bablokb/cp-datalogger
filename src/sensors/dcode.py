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
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

SENSOR_MAP = {
  "id":      "0",
  "dcode":   "1",
  "battery": "2",
  "aht20":   "3",
  "am2320":  "4",
  "bh1750":  "5",
  "bme280":  "6",
  "bmp280":  "7",
  "ds18b20": "8",
  "ens160":  "9",
  "htu31d":  "A",
  "ltr559":  "B",
  "mcp9808": "C",
  "pdm":     "D",
  "pms5003": "E",
  "scd40":   "F",
  "scd41":   "G",
  "sht45":   "H",
  "meteo":   "I",
  "location": "J"
  }

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
