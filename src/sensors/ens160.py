#-----------------------------------------------------------------------------
# Sensor definition for ENS160.
#
# Naming convention:
#   - filenames in lowercase (ens160.py)
#   - class name the same as filename in uppercase (ENS160)
#   - the constructor must take four arguments (config,i2c,addr,spi)
#     and probe for the device
#   - the read-method must update the data and return a string with the
#     values for the csv-record
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

# Important notes:
#
# The sensor needs an initial run in period of at least 48 hours.
#
# After POR, the sensor needs a warmup period of about 3 minutes.
#
# This implementation will:
#   - return the warmup-status and no data for continuous-mode
#   - will trigger a deep sleep for the expected warmup period for strobe-mode
# This strategy assumes that in continuous-mode the system is running on
# USB-power. In strobe-mode, the deep sleep will at least minimize the
# battery drain (with CP 8.0.5: 6.3mA).
#
# eCO2 seems to be highly correlated to TVOC, so eCO2 is actually
# redundant to judge air-quality. The AQI itself is highly questionable,
# because it is calculated on an absolute scale which is not globally
# valid for all measurement patterns. If you really want to use AQI,
# think about taking a measurement after 180 seconds.
#
# Otherwise, the sensor is fine and shows a good reaction to ventilation.

# Default configuration. Override with ENS160_xxx in config.py.

INTERVALS  = [0,5]             # interval between readings
DISCARD    = True              # only keep last reading
WARMUP     = 190               # warmup time in seconds (for status==1)
PROPERTIES = "AQI TVOC eCO2"   # properties for the display

from log_writer import Logger
g_logger = Logger()

import time
import adafruit_ens160

from sleep import TimeSleep

class ENS160:

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """

    self.ignore = False
    self.ens160 = None
    for nr,bus in enumerate(i2c):
      if not bus:
        continue
      try:
        g_logger.print(f"testing ens160 on i2c{nr}")
        self.ens160 = adafruit_ens160.ENS160(bus,reset=False)
        g_logger.print(f"detected ens160 on i2c{nr}")
        break
      except Exception as ex:
        g_logger.print(f"exception: {ex}")
    if not self.ens160:
      raise Exception("no ens160 detected. Check config/cabling!")

    self.STROBE_MODE = config.STROBE_MODE
    self.DISCARD     = getattr(config,"ENS160_DISCARD",DISCARD)
    self.INTERVALS   = getattr(config,"ENS160_INTERVALS",INTERVALS)
    self.WARMUP      = getattr(config,"ENS160_WARMUP",WARMUP)
    self.PROPERTIES  = getattr(config,"ENS160_PROPERTIES",PROPERTIES).split()

    # dynamically create formats for display...
    self.formats = []
    for p in self.PROPERTIES:
      self.formats.extend([f"{p}:","{0}"])

    # ... and header for csv
    self.headers = 'status'
    if DISCARD:
      self.headers += f",AQI,TVOC ppb,eCO2 ppm eq."
    else:
      for i in range(len(self.INTERVALS)):
        self.headers += f",AQI ({i+1}),TVOC ppb ({i+1}),eCO2 ppm eq. ({i+1})"

  def read(self,data,values):
    status = self.ens160.data_validity

    # initial startup or invalid data
    if status > 1:
      g_logger.print("ens160: initial startup or invalid data!")
      if not self.ignore:
        for _ in self.PROPERTIES:
          values.extend([None,0])
      return f"{status},0,0,0"

    # warmup: in strobe-mode we restart the system later, otherwise only
    #         return status information
    if status == 1:
      if self.STROBE_MODE:
        g_logger.print(
          f"ens160: warmup - deep-sleep for {self.WARMUP}s")
        TimeSleep.deep_sleep(duration=self.WARMUP)
      else:
        g_logger.print("ens160: initial warmup!")
        if not self.ignore:
          for _ in self.PROPERTIES:
            values.extend([None,0])
        return f"{status},0,0,0"

    # normal operation
    if status == 0:
      g_logger.print("ens160: normal operation")
      if "aht20" in data:
        self.ens160.temperature_compensation = data["aht20"]["t"]
        self.ens160.humidity_compensation    = data["aht20"]["h"]

      # take multiple readings
      csv_results = f"{status}"
      for i in range(len(self.INTERVALS)):
        TimeSleep.light_sleep(duration=self.INTERVALS[i])
        #status == 0 might still not provide valid data
        while True:
          while not self.ens160.new_data_available:
            g_logger.print("ens160: waiting for data...")
            time.sleep(0.2)
          ens_data = self.ens160.read_all_sensors()
          if not ens_data['eCO2'] is None:
            break
        if not self.DISCARD or i == len(self.INTERVALS)-1:
          csv_results += (
            f",{ens_data['AQI']},{ens_data['TVOC']},{ens_data['eCO2']}")

      # only show last reading on display
      data["ens160"] = ens_data
      if not self.ignore:
        for p in self.PROPERTIES:
          values.extend([None,ens_data[p]])
      return csv_results
