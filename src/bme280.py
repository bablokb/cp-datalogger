#-----------------------------------------------------------------------------
# Sensor definition for BME280.
#
# Naming convention:
#   - filenames in lowercase (bme280.py)
#   - class name the same as filename in uppercase (BME280)
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

from adafruit_bme280 import advanced as adafruit_bme280

class BME280:
  formats = ["T/BME:", "{0:.1f}°C",
             "H/BME:", "{0:.0f}%rH",
             "P/BME:", "{0:.0f}hPa"]
  headers = 'T/BME °C,H/BME %rH,P/BME'

  def __init__(self,config,i2c0=None,i2c1=None,spi0=None,spi1=None):
    """ constructor """
    try:
      if i2c1:
        g_logger.print("testing bme280 on i2c1")
        self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(
          i2c1,address=0x76)
        g_logger.print("detected bme280 on i2c1")
    except Exception as ex:
      g_logger.print(f"exception: {ex}")
      if i2c0:
        g_logger.print("testing bme280 on i2c0")
        self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(
          i2c0,address=0x76)
        g_logger.print("detected bme280 on i2c0")

    self.bme280.mode                 = adafruit_bme280.MODE_SLEEP
    self.bme280.iir_filter           = adafruit_bme280.IIR_FILTER_DISABLE
    self.bme280.overscan_pressure    = adafruit_bme280.OVERSCAN_X1
    self.bme280.overscan_humidity    = adafruit_bme280.OVERSCAN_X1
    self.bme280.overscan_temperature = adafruit_bme280.OVERSCAN_X1

    if hasattr(config,"BMx280_ALTITUDE_AT_LOCATION"):
      altitude = config.BMx280_ALTITUDE_AT_LOCATION
    else:
      altitude = 525
    self.alt_factor = pow(1.0-altitude/44330.0, 5.255)

  def read(self,data,values):
    """ read sensor """
    self.bme280.mode = adafruit_bme280.MODE_FORCE
    t = self.bme280.temperature
    p = self.bme280.pressure/self.alt_factor
    h = self.bme280.humidity
    data["bme280"] = {
      "temp": t,
      "hum":  h,
      "pressure": p
    }
    values.extend([None,t])
    values.extend([None,h])
    values.extend([None,p])
    return f"{t:0.1f},{h:0.0f},{p:0.0f}"
