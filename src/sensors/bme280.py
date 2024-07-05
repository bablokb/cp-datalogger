#-----------------------------------------------------------------------------
# Sensor definition for BME280.
#
# Naming convention:
#   - filenames in lowercase (bme280.py)
#   - class name the same as filename in uppercase (BME280)
#   - the constructor must take four arguments (config,i2c,addr,spi)
#     and probe for the device
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

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """

    self.ignore = False
    self.bme280 = None
    address = addr if addr else 0x76
    for bus,nr in i2c:
      try:
        g_logger.print(f"testing bme280 on (i2c{nr},{address})")
        self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(
          bus,address=address)
        g_logger.print(f"detected bme280 on (i2c{nr},{address})")
        break
      except Exception as ex:
        g_logger.print(f"exception: {ex}")
    if not self.bme280:
      raise Exception("no bme280 detected. Check config/cabling!")

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
    t = round(self.bme280.temperature,1)
    p = round(self.bme280.pressure/self.alt_factor,0)
    h = round(self.bme280.humidity,0)
    data["bme280"] = {
      "temp": t,
      "hum":  h,
      "pressure": p
    }
    if not self.ignore:
      values.extend([None,t])
      values.extend([None,h])
      values.extend([None,p])
    return f"{t:0.1f},{h:0.0f},{p:0.0f}"
