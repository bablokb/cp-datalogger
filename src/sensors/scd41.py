#-----------------------------------------------------------------------------
# Sensor definition for SCD41.
#
# Naming convention:
#   - filenames in lowercase (scd41.py)
#   - class name the same as filename in uppercase (SCD41)
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
DISCARD = True                # only keep last reading

from log_writer import Logger
g_logger = Logger()

import time
from .scd4x import SCD4X

class SCD41(SCD4X):
  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """
    self.product = "scd41"
    super().__init__(config,i2c,addr,spi)

  def read_sensor(self):
    """ quer data from sensor """
    self.scd4x.measure_single_shot()
