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

from log_writer import Logger
g_logger = Logger()

import busio
import time
import pins
from adafruit_pm25.uart import PM25_UART
from adafruit_pm25.i2c  import PM25_I2C

from sleep import TimeSleep

class PMS5003:
  formats = ["PM0.3:", "{0}","PM1.0:", "{0}","PM2.5:", "{0}"]
  headers = 'PM0.3,PM1.0,PM2.5'

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """
    self.ignore = False
    self.pms5003 = None
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

  def read(self,data,values):
    """ read sensor """
    # take first measurement at least 30s after power-up
    wtime = max(30-int(time.monotonic()),0)
    if wtime > 0:
      g_logger.print(f"pms5003: waiting {wtime}s for first measurement")
      TimeSleep.light_sleep(wtime)

    # retry until read does not throw an exception
    # TODO: limit retries
    while True:
      try:
        pms5003_data = self.pms5003.read()
        break
      except:
        g_logger.print("pms5003: read failed with exception")
        time.sleep(0.1)

    pm03 = pms5003_data["particles 03um"]
    pm10 = pms5003_data["particles 10um"]
    pm25 = pms5003_data["particles 25um"]

    data["pms5003"] = {
      "p03": pm03,
      "p10": pm10,
      "p25": pm25,
      self.formats[0]: self.formats[1].format(pm03),
      self.formats[2]: self.formats[3].format(pm10),
      self.formats[4]: self.formats[5].format(pm25)
      }
    if not self.ignore:
      values.extend([None,pm03])
      values.extend([None,pm10])
      values.extend([None,pm25])
    return f"{pm03},{pm10},{pm25}"
