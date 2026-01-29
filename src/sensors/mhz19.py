#-----------------------------------------------------------------------------
# Sensor definition for MHZ19. The code assumes the MHZ19 is attached via UART.
#
# Naming convention:
#   - filenames in lowercase (mhz19.py)
#   - class name the same as filename in uppercase (MHZ19)
#   - the constructor must take four arguments (config,i2c,addr,spi)
#     and probe for the device
#   - the read-method must update the data and return a string with the
#     values for the csv-record
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

PROPERTIES = "c t"          # properties for the display
RETRIES = 3                 # retries for data readout
INIT_TIME = 60              # manual 1.2: 60s, (older) manual 1.21: 150s
AUTO_CALIB = False
FORMATS = {
  "c": ["C/MHZ:","{0}p"],
  "t": ["T/MHZ:", "{0:.1f}°C"]
}

from log_writer import Logger
g_logger = Logger()

import busio
import time
import pins
import mhz19

from sleep import TimeSleep

class MHZ19:
  headers = 'C/MHZ ppm,T/MHZ °C'

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """
    self.ignore = False
    self.mhz19 = None

    # query parameters
    self.PROPERTIES = getattr(config,"MHZ19_PROPERTIES",PROPERTIES).split()
    self.RETRIES    = getattr(config,"MHZ19_RETRIES",RETRIES)
    self.init_time  = getattr(config,"MHZ19_INIT_TIME",INIT_TIME)
    self.auto_calib = getattr(config,"MHZ19_AUTO_CALIB",AUTO_CALIB)

    uart = busio.UART(pins.PIN_TX, pins.PIN_RX, baudrate=9600, timeout=10)
    self.mhz19 = mhz19.MHZ19(uart)
    self.mhz19.autocalibration = self.auto_calib
    
    self.formats = []
    for p in self.PROPERTIES:
      self.formats.extend(FORMATS[p])

  def read(self,data,values):
    """ read sensor """
    # take first measurement at least INIT_TIMEs after power-up
    wtime = max(self.init_time-int(time.monotonic()),0)
    if wtime > 0:
      g_logger.print(f"mhz19: waiting {wtime}s for first measurement")
      TimeSleep.light_sleep(wtime)

    # retry until read does not throw an exception
    # TODO: limit retries
    i = 0
    while i < self.RETRIES:
      try:
        mhz19_data = self.mhz19.read()
        break
      except Exception as ex:
        g_logger.print(f"mhz19: read failed with exception: {ex}")
        i += 1
        time.sleep(0.1)

    if i == self.RETRIES:
      co2 = temp = 0
    else:
      co2  = mhz19_data[0]
      temp = mhz19_data[1]

    data["mhz19"] = {
      "c": co2,
      "t": temp,
      FORMATS['c'][0]: FORMATS['c'][1].format(co2),
      FORMATS['t'][0]: FORMATS['t'][1].format(temp),
      }
    if not self.ignore:
      for p in self.PROPERTIES:
        values.extend([None,data["mhz19"][p]])
    return f"{co2},{temp:.1f}"
