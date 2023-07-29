#-----------------------------------------------------------------------------
# Sensor definition for ENS160.
#
# Naming convention:
#   - filenames in lowercase (ens160.py)
#   - class name the same as filename in uppercase (ENS160)
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

# Important notes:
#
# A reading of the sensor right after startup is more or less useless.
# After about 60s, the readings are stable. Nevertheless, taking
# readings earlier is a good compromise between accuracy and
# current consumption. You just cannot use absolute values but should
# use relative values compared to a well known baseline.
#
# eCO2 seems to be highly correlated to TVOC, so eCO2 is actually
# redundant to judge air-quality. The AQI itself is highly questionable,
# because it is calculated on an absolute scale which is not globally
# valid for all measurement patterns. If you really want to use AQI,
# think about taking a measurement after 180 seconds.
#
# Otherwise, the sensor is fine and shows a good reaction to ventilation.

# we could put this into the global configuration, but since changing
# this is only for experimental purposes, we don't pollute config.py

MEASUREMENT_INTERVALS = [0,5] # interval between readings
DISCARD = True                # only keep last reading

from log_writer import Logger
g_logger = Logger()

import time
import adafruit_ens160

class ENS160:
  # don't print status on display, but add to csv
  formats = ["AQI:", "{0}",
             "TVOC:", "{0}",
             "eCO2:", "{0}"
             ]
  headers = 'status'
  if DISCARD:
    headers += f",AQI,TVOC ppb,eCO2 ppm eq."
  else:
    for i in range(len(MEASUREMENT_INTERVALS)):
      headers += f",AQI ({i+1}),TVOC ppb ({i+1}),eCO2 ppm eq. ({i+1})"

  def __init__(self,config,i2c0=None,i2c1=None,
               addr=None,bus=None,
               spi0=None,spi1=None):
    """ constructor """

    self.ens160 = None
    if bus:
      busses = [bus]
    else:
      busses = [i2c1,i2c0]
    for bus in busses:
      try:
        if bus:
          g_logger.print(f"testing ens160 on {str(bus)}")
          self.ens160 = adafruit_ens160.ENS160(bus)
          g_logger.print(f"detected ens160 on {str(bus)}")
          break
      except Exception as ex:
        g_logger.print(f"exception: {ex}")
    if not self.ens160:
      raise Exception("no ens160 detected. Check config/cabling!")

  def read(self,data,values):
    status = self.ens160.data_validity

    # initial startup or invalid data
    if status > 1:
      g_logger.print("ens160: initial startup or invalid data!")
      values.extend([None,status])
      values.extend([None,0])
      values.extend([None,0])
      values.extend([None,0])
      return f"{ens_data['status']},0,0,0"

    # warmup
    if status == 1:
      sleep_time = 120
      while status == 1:
        g_logger.print(f"ens160: warmup - sleeping {sleep_time}s}")
        time.sleep(sleep_time)
        sleep_time = max(sleep_time/2,10)
        status = self.ens160.data_validity

    # normal operation
    if status == 0:
      g_logger.print("ens160: normal operation")
      if "aht20" in data:
        self.ens160.temperature_compensation = data["aht20"]["temp"]
        self.ens160.humidity_compensation    = data["aht20"]["hum"]

      # take multiple readings
      csv_results = f"{status}"
      for i in range(len(MEASUREMENT_INTERVALS)):
        time.sleep(MEASUREMENT_INTERVALS[i])
        #status == 0 might still not provide valid data
        while True:
          while not self.ens160.new_data_available:
            g_logger.print("ens160: waiting for data...")
            time.sleep(0.2)
          ens_data = self.ens160.read_all_sensors()
          if not ens_data['eCO2'] is None:
            break
        if not DISCARD or i == len(MEASUREMENT_INTERVALS)-1:
          csv_results += (
            f",{ens_data['AQI']},{ens_data['TVOC']},{ens_data['eCO2']}")

      # only show last reading on display
      data["ens160"] = ens_data
      values.extend([None,ens_data['AQI']])
      values.extend([None,ens_data['TVOC']])
      values.extend([None,ens_data['eCO2']])
      return csv_results
