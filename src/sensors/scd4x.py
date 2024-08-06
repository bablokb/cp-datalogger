#-----------------------------------------------------------------------------
# Base class for Sensor definitions for SCD40/SCD41. Don't use this class
# directly!
#
# Naming convention:
#   - filenames in lowercase (scd4x.py)
#   - class name the same as filename in uppercase (SCD4X)
#   - the constructor must take four arguments (config,i2c,addr,spi)
#     and probe for the device
#   - the read-method must update the data and return a string with the
#     values for the csv-record
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

SAMPLES = 2
TIMEOUT = 10                  # data should be ready every 5 seconds
DISCARD = True                # only keep last reading
PROPERTIES = "c t h"          # properties for the display
FORMATS = {
  "c":   ["C/SCD:", "{0}p"],
  "t":   ["T/SCD:", "{0:.1f}°C"],
  "h":   ["H/SCD:", "{0:.0f}%rH"]
  }

from log_writer import Logger
g_logger = Logger()

import time
import adafruit_scd4x

class SCD4X:
  # we don't use timestamps on the display ...
  headers = 'C/SCD ppm,T/SCD °C,H/SCD %rH'

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """

    self._config = config
    self.ignore = False
    self.init_time = 5
    self.scd4x = None
    for nr,bus in enumerate(i2c):
      if not bus:
        continue
      try:
        g_logger.print(f"testing {self.product} on i2c{nr}")
        self.scd4x = adafruit_scd4x.SCD4X(bus)
        g_logger.print(f"detected {self.product} on i2c{nr}")
        break
      except Exception as ex:
        g_logger.print(f"exception: {ex}")
    if not self.scd4x:
      raise Exception(f"no {self.product} detected. Check config/cabling!")

    self.SAMPLES = getattr(config,"SCD4X_SAMPLES",SAMPLES)
    self.TIMEOUT = getattr(config,"SCD4X_TIMEOUT",TIMEOUT)
    self.DISCARD = getattr(config,"SCD4X_DISCARD",DISCARD)
    self.PROPERTIES = getattr(config,"SCD4X_PROPERTIES",PROPERTIES).split()

    # dynamically create formats for display...
    self.formats = []
    for p in self.PROPERTIES:
      self.formats.extend(FORMATS[p])

    # ... and header for csv
    if not self.DISCARD:
      self.headers = 't (1),CO2 ppm (1)'
      for i in range(1,self.SAMPLES):
        self.headers += f",t ({i+1}),CO2 ppm ({i+1})"
      self.headers += ',T/SCD °C,H/SCD %rH'

  def read_sensor(self):
    """ dummy method, must be implemented by subclass if necessary """
    pass

  def read(self,data,values):
    # take multiple readings
    csv_results = ""
    t0 = time.monotonic()
    for i in range(self.SAMPLES):
      g_logger.print(f"{self.product}: waiting for data...")
      t_rel = 0
      co2   = 0
      temp  = 0
      hum   = 0
      start = time.monotonic()
      while time.monotonic()-start < self.TIMEOUT:
        self.read_sensor()
        if self.scd4x.data_ready:
          t_rel = time.monotonic() - t0
          co2   = self.scd4x.CO2
          temp  = round(self.scd4x.temperature,1)
          hum   = round(self.scd4x.relative_humidity,0)
          g_logger.print(f"{self.product}: CO2 at {t_rel:.2f}: {co2}")
          if not self.DISCARD:
            csv_results += f",{t_rel:.2f},{co2}"
          break
        else:
          time.sleep(0.2)

    # switch sensor off in strobe mode (or cont. mode with deep-sleep)
    if self._config.STROBE_MODE or self._config.INTERVAL > 60:
      self.scd4x.stop_periodic_measurement()

    # only keep last reading for CSV if DISCARD is active
    if self.DISCARD:
      csv_results = f",{co2}"
    csv_results += f",{temp:.1f},{hum:.0f}"

    # in any case, only show last reading on display
    data[self.product] = {
      "t": temp,
      "h":  hum,
      "c":  co2,
      FORMATS['t'][0]: FORMATS['t'][1].format(temp),
      FORMATS['h'][0]: FORMATS['h'][1].format(hum),
      FORMATS['c'][0]: FORMATS['c'][1].format(co2)
    }
    if not self.ignore:
      for p in self.PROPERTIES:
        values.extend([None,data[self.product][p]])
    return csv_results[1:]
