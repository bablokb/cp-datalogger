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
  headers = 'status,AQI,TVOC ppb,eCO2 ppm eq.'

  def __init__(self,config,i2c0=None,i2c1=None,spi0=None,spi1=None):
    """ constructor """
    try:
      if i2c1:
        g_logger.print("testing ens160 on i2c1")
        self.ens160 = adafruit_ens160.ENS160(i2c1)
        g_logger.print("detected ens160 on i2c1")
    except Exception as ex:
      g_logger.print(f"exception: {ex}")
      if i2c0:
        g_logger.print("testing ens160 on i2c0")
        self.ens160 = adafruit_ens160.ENS160(i2c0)
        g_logger.print("detected ens160 on i2c0")

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

      #status == 0 might still not provide valid data
      while True:
        while not self.ens160.new_data_available:
          g_logger.print("ens160: waiting for data...")
          time.sleep(0.2)
        ens_data = self.ens160.read_all_sensors()
        if not ens_data['eCO2'] is None:
          break

      data["ens160"] = ens_data
      values.extend([None,ens_data['AQI']])
      values.extend([None,ens_data['TVOC']])
      values.extend([None,ens_data['eCO2']])
      return f"{status},{ens_data['AQI']},{ens_data['TVOC']},{ens_data['eCO2']}"
