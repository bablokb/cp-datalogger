#-----------------------------------------------------------------------------
# Sensor definition for BMP280.
#
# Naming convention:
#   - filenames in lowercase (bmp280.py)
#   - class name the same as filename in uppercase (BMP280)
#   - the constructor must take four arguments (config,i2c,addr,spi)
#     and probe for the device
#   - the read-method must update the data and return a string with the
#     values for the csv-record
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

PROPERTIES = "t ps"          # properties for the display
FORMATS = {
  "t": ["T/BMP:", "{0:.1f}°C"],
  "ps": ["P/BMP:", "{0:.0f}hPa"]
  }

from log_writer import Logger
g_logger = Logger()

import adafruit_bmp280

class BMP280:
  headers = 'T/BMP °C,P/BMP'

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """

    self.ignore = False
    self.bmp280 = None
    address = addr if addr else 0x77
    for nr,bus in enumerate(i2c):
      if not bus:
        continue
      try:
        g_logger.print(f"testing bmp280 on (i2c{nr},{address})")
        self.bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(
          bus,address=address)
        g_logger.print(f"detected bmp280 on (i2c{nr},{address})")
        break
      except Exception as ex:
        g_logger.print(f"exception: {ex}")
    if not self.bmp280:
      raise Exception("no bmp280 detected. Check config/cabling!")

    self.bmp280.mode                 = adafruit_bmp280.MODE_SLEEP
    self.bmp280.iir_filter           = adafruit_bmp280.IIR_FILTER_DISABLE
    self.bmp280.overscan_pressure    = adafruit_bmp280.OVERSCAN_X1
    self.bmp280.overscan_temperature = adafruit_bmp280.OVERSCAN_X1

    # dynamically create formats for display...
    self.PROPERTIES = getattr(config,"BMP280_PROPERTIES",PROPERTIES).split()
    self.formats = []
    for p in self.PROPERTIES:
      self.formats.extend(FORMATS[p])

    if hasattr(config,"BMx280_ALTITUDE_AT_LOCATION"):
      altitude = config.BMx280_ALTITUDE_AT_LOCATION
    else:
      altitude = 525
    self.alt_factor = pow(1.0-altitude/44330.0, 5.255)

  def read(self,data,values):
    """ read sensor """
    self.bmp280.mode = adafruit_bmp280.MODE_FORCE
    t  = round(self.bmp280.temperature,1)
    ps = round(self.bmp280.pressure/self.alt_factor,0)
    data["bmp280"] = {
      "t": t,
      "ps": ps,
      FORMATS['t'][0]: FORMATS['t'][1].format(t),
      FORMATS['ps'][0]: FORMATS['ps'][1].format(ps)
    }
    if not self.ignore:
      for p in self.PROPERTIES:
        values.extend([None,data["bmp280"][p]])
    return f"{t:0.1f},{ps:0.0f}"
