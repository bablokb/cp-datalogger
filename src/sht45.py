#-----------------------------------------------------------------------------
# Sensor definition for SHT45.
#
# Naming convention:
#   - filenames in lowercase (sht45.py)
#   - class name the same as filename in uppercase (SHT45)
#   - the constructor must take five arguments (config,i2c0,ic1,spi0,spi1)
#     and probe for the device
#   - i2c1 is the default i2c-device and should be probed first
#   - the read-method must update the data and return a string with the
#     values for the csv-record
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

from log_writer import Logger
g_logger = Logger()

import adafruit_sht4x

class SHT45:
  formats = ["T/SHT:", "{0:.1f}°C","H/SHT:", "{0:.0f}%rH"]
  headers = 'T/SHT °C,H/SHT %rH'

  def __init__(self,config,i2c0=None,i2c1=None,
               addr=None,bus=None,
               spi0=None,spi1=None):
    """ constructor """

    self.sht45 = None
    _busses = [i2c0,i2c1]
    if not bus is None:
      bus_nr = [bus]
    else:
      bus_nr = [1,0]
    for nr in bus_nr:
      try:
        bus = _busses[nr]
        if bus:
          g_logger.print(f"testing sht45 on i2c{nr}")
          self.sht45 = adafruit_sht4x.SHT4x(bus)
          g_logger.print(f"detected sht45 on i2c{nr}")
          break
      except Exception as ex:
        g_logger.print(f"exception: {ex}")
    if not self.sht45:
      raise Exception("no sht45 detected. Check config/cabling!")

  def read(self,data,values):
    """ read sensor """
    t = self.sht45.temperature
    h = self.sht45.relative_humidity
    data["sht45"] = {
      "temp": t,
      "hum":  h
    }
    values.extend([None,t])
    values.extend([None,h])
    return f"{t:0.1f},{h:0.0f}"
