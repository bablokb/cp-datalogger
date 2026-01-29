#-----------------------------------------------------------------------------
# Sensor definition for SCD40.
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
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

SAMPLES = 2
DISCARD = True                # only keep last reading

from log_writer import Logger
g_logger = Logger()

import time
from .scd4x import SCD4X

class SCD40(SCD4X):
  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """

    self.product = "scd40"
    super().__init__(config,i2c,addr,spi)
