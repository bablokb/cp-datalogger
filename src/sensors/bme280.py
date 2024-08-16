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

PROPERTIES = "t h pl ps"          # properties for the display
FORMATS = {
  "t":  ["T/BME:",  "{0:.1f}°C"],   # temperature
  "h":  ["H/BME:",  "{0:.0f}%rH"],  # humidity
  "pl": ["Pl/BME:", "{0:.0f}hPa"],  # pressure at location
  "ps": ["Ps/BME:", "{0:.0f}hPa"]   # pressure at sea-level (converted)
  }

from log_writer import Logger
g_logger = Logger()

from adafruit_bme280 import advanced as adafruit_bme280

class BME280:
  headers = 'T/BME °C,H/BME %rH,Pl/BME,Ps/BME'

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """

    self.ignore = False
    self.bme280 = None
    address = addr if addr else 0x76
    for nr,bus in enumerate(i2c):
      if not bus:
        continue
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

    # dynamically create formats for display...
    self.PROPERTIES = getattr(config,"BME280_PROPERTIES",PROPERTIES).split()
    self.formats = []
    for p in self.PROPERTIES:
      self.formats.extend(FORMATS[p])

    self.bme280.mode                 = adafruit_bme280.MODE_SLEEP
    self.bme280.iir_filter           = adafruit_bme280.IIR_FILTER_DISABLE
    self.bme280.overscan_pressure    = adafruit_bme280.OVERSCAN_X1
    self.bme280.overscan_humidity    = adafruit_bme280.OVERSCAN_X1
    self.bme280.overscan_temperature = adafruit_bme280.OVERSCAN_X1

    if hasattr(config,"BMx280_ALTITUDE_AT_LOCATION"):
      altitude = config.BMx280_ALTITUDE_AT_LOCATION
    else:
      altitude = 540
    self.alt_factor = pow(1.0-altitude/44330.0, 5.255)

  def read(self,data,values):
    """ read sensor """
    self.bme280.mode = adafruit_bme280.MODE_FORCE
    t  = round(self.bme280.temperature,1)
    h  = round(self.bme280.humidity,0)
    pl = self.bme280.pressure
    ps = round(pl/self.alt_factor,0)
    pl = round(pl,0)
    data["bme280"] = {
      "t": t,
      "h":  h,
      "pl": pl,
      "ps": ps,
      FORMATS['t'][0]: FORMATS['t'][1].format(t),
      FORMATS['h'][0]: FORMATS['h'][1].format(h),
      FORMATS['pl'][0]: FORMATS['pl'][1].format(pl),
      FORMATS['ps'][0]: FORMATS['ps'][1].format(ps)
    }
    if not self.ignore:
      for p in self.PROPERTIES:
        values.extend([None,data["bme280"][p]])
    return f"{t:0.1f},{h:0.0f},{pl:0.0f},{ps:0.0f}"
