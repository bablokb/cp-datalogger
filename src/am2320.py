#-----------------------------------------------------------------------------
# Sensor definition for AM2320.
#
# Naming convention:
#   - filenames in lowercase (am2320.py)
#   - class name the same as filename in uppercase (AM2320)
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

class AM2320:
  formats = ["T/AM:", "{0:.1f}°C","H/AM:", "{0:.0f}%rH"]
  headers = 'T/AM °C,H/AM %rH'

  def __init__(self,config,i2c0=None,i2c1=None,spi0=None,spi1=None):
    """ constructor """
    import adafruit_am2320
    try:
      if i2c1:
        g_logger.print("testing am2320 on i2c1")
        self.am2320 = adafruit_am2320.AM2320(i2c1)
        g_logger.print("detected am2320 on i2c1")
    except Exception as ex:
      g_logger.print(f"exception: {ex}")
      if i2c0:
        g_logger.print("testing am2320 on i2c0")
        self.am2320 = adafruit_am2320.AM2320(i2c0)
        g_logger.print("detected am2320 on i2c0")

  def read(self,data,values):
    """ read sensor """
    t = self.am2320.temperature
    h = self.am2320.relative_humidity
    data["am2320"] = {
      "temp": t,
      "hum":  h
    }
    values.extend([None,t])
    values.extend([None,h])
    return f"{t:0.1f},{h:0.0f}"
