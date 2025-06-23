#-----------------------------------------------------------------------------
# Sensor definition for PMS5003. The code first checks for I2C-devices.
# If no I2C is detected, the code assumes a PMS5003 attached via UART.
#
# Naming convention:
#   - filenames in lowercase (pms5003.py)
#   - class name the same as filename in uppercase (PMS5003)
#   - the constructor must take four arguments (config,i2c,addr,spi)
#     and probe for the device
#   - the read-method must update the data and return a string with the
#     values for the csv-record
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

PROPERTIES = "pn03 pn10 pn25"       # properties for the display
PN_FACTOR  = 0.01                   # conversion factor for particles
RETRIES = 3                         # retries for data readout
FORMATS = {
  "pm10": ["PM1.0/PMS:","{0}"],         # 0-500 µg/m³ effective range
  "pm25": ["PM2.5/PMS:","{0}"],         # 0-500 µg/m³ effective range
  "pm100": ["PM10/PMS:","{0}"],         # 0-500 µg/m³ effective range (estimated)

  "pn03": ["PN0.3/PMS:","{0}"],         # particles/100cm³
  "pn05": ["PN0.5/PMS:","{0}"],         # particles/100cm³
  "pn10": ["PN1.0/PMS:","{0}"],         # particles/100cm³
  "pn25": ["PN2.5/PMS:","{0}"],         # particles/100cm³
  "pn50": ["PN5.0/PMS:","{0}"],         # particles/100cm³ (estimated)
  "pn100": ["PN10/PMS:","{0}"]          # particles/100cm³ (estimated)
}

from log_writer import Logger
g_logger = Logger()

import busio
import time
import pins
from adafruit_pm25.uart import PM25_UART
from adafruit_pm25.i2c  import PM25_I2C

from sleep import TimeSleep

class PMS5003:
  HEADERS_PM   = 'PM1.0,PM2.5,PM10'
  HEADERS_PN   = 'PN0.3,PN0.5,PN1.0,PN2.5,PN5.0,PN10'
  HEADERS      = ','.join([HEADERS_PM,HEADERS_PN])

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """
    self.ignore = False
    self.pms5003 = None
    self.init_time = 30
    self.headers = PMS5003.HEADERS
    for nr,bus in enumerate(i2c):
      if not bus:
        continue
      try:
        g_logger.print(f"testing pms5003 on i2c{nr}")
        self.pms5003 = PM25_I2C(bus)
        g_logger.print(f"detected pms5003 on i2c{nr}")
        break
      except Exception as ex:
        g_logger.print(f"exception: {ex}")
    if not self.pms5003:
      g_logger.print("no pms5003 on I2C detected. Falling back to UART")
      uart = busio.UART(pins.PIN_TX, pins.PIN_RX, baudrate=9600)
      self.pms5003 = PM25_UART(uart,None)

    # dynamically create formats for display...
    self.PROPERTIES = getattr(config,"PMS5003_PROPERTIES",PROPERTIES).split()
    self.RETRIES    = getattr(config,"PMS5003_RETRIES",RETRIES)
    self.PN_FACTOR  = getattr(config,"PMS5003_PN_FACTOR",PN_FACTOR)
    self.formats = []
    for p in self.PROPERTIES:
      self.formats.extend(FORMATS[p])

  def read(self,data,values):
    """ read sensor """

    # retry until read does not throw an exception
    # TODO: limit retries
    i = 0
    while i < self.RETRIES:
      try:
        pms5003_data = self.pms5003.read()
        break
      except:
        g_logger.print("pms5003: read failed with exception")
        i += 1
        time.sleep(0.1)

    if i == self.RETRIES:
      pm10 = -1; pm25 = -1; pm100 = -1
      pn03 = -1; pn05 = -1; pn10 = -1; pn25 = -1; pn50 = -1; pn100 = -1
    else:
      pm10  = pms5003_data["pm10 env"]
      pm25  = pms5003_data["pm25 env"]
      pm100 = pms5003_data["pm100 env"]

      pn03  = pms5003_data["particles 03um"] * self.PN_FACTOR
      pn05  = pms5003_data["particles 05um"] * self.PN_FACTOR
      pn10  = pms5003_data["particles 10um"] * self.PN_FACTOR
      pn25  = pms5003_data["particles 25um"] * self.PN_FACTOR
      pn50  = pms5003_data["particles 50um"] * self.PN_FACTOR
      pn100 = pms5003_data["particles 100um"] * self.PN_FACTOR

    data["pms5003"] = {
      "pm10": pm10,
      "pm25": pm25,
      "pm100": pm100,

      "pn03": pn03,
      "pn05": pn05,
      "pn10": pn10,
      "pn25": pn25,
      "pn50": pn50,
      "pn100": pn100,
      FORMATS['pm10'][0]: FORMATS['pm10'][1].format(pm10),
      FORMATS['pm25'][0]: FORMATS['pm25'][1].format(pm25),
      FORMATS['pm100'][0]: FORMATS['pm100'][1].format(pm100),

      FORMATS['pn03'][0]: FORMATS['pn03'][1].format(pn03),
      FORMATS['pn05'][0]: FORMATS['pn05'][1].format(pn05),
      FORMATS['pn10'][0]: FORMATS['pn10'][1].format(pn10),
      FORMATS['pn25'][0]: FORMATS['pn25'][1].format(pn25),
      FORMATS['pn50'][0]: FORMATS['pn50'][1].format(pn50),
      FORMATS['pn100'][0]: FORMATS['pn100'][1].format(pn100),
      }
    if not self.ignore:
      for p in self.PROPERTIES:
        values.extend([None,data["pms5003"][p]])
    return f"{pm10},{pm25},{pm100},{pn03},{pn05},{pn10},{pn25},{pn50},{pn100}"
