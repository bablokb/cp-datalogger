#-----------------------------------------------------------------------------
# Sensor definition for BMP280.
#
# Naming convention:
#   - filenames in lowercase (bmp280.py)
#   - class name the same as filename in uppercase (BMP280)
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

import adafruit_bmp280

class BMP280:
  formats = ["T/BMP:", "{0:.1f}°C",
             "P/BMP:", "{0:.0f}hPa"]
  headers = 'T/BMP °C,P/BMP'

  def __init__(self,config,i2c0=None,i2c1=None,spi0=None,spi1=None):
    """ constructor """
    try:
      if i2c1:
        g_logger.print("testing bmp280 on i2c1")
        self.bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(
          i2c1,address=0x77)
        g_logger.print("detected bmp280 on i2c1")
    except Exception as ex:
      g_logger.print(f"exception: {ex}")
      if i2c0:
        g_logger.print("testing bmp280 on i2c0")
        self.bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(
          i2c0,address=0x77)
        g_logger.print("detected bmp280 on i2c0")

    self.bmp280.mode                 = adafruit_bmp280.MODE_SLEEP
    self.bmp280.iir_filter           = adafruit_bmp280.IIR_FILTER_DISABLE
    self.bmp280.overscan_pressure    = adafruit_bmp280.OVERSCAN_X1
    self.bmp280.overscan_temperature = adafruit_bmp280.OVERSCAN_X1

    if hasattr(config,"BMx280_ALTITUDE_AT_LOCATION"):
      altitude = config.BMx280_ALTITUDE_AT_LOCATION
    else:
      altitude = 525
    self.alt_factor = pow(1.0-altitude/44330.0, 5.255)

  def read(self,data,values):
    """ read sensor """
    self.bmp280.mode = adafruit_bmp280.MODE_FORCE
    t = self.bmp280.temperature
    p = self.bmp280.pressure/self.alt_factor
    data["bmp280"] = {
      "temp": t,
      "pressure": p
    }
    values.extend([None,t])
    values.extend([None,p])
    return f"{t:0.1f},{p:0.0f}"
