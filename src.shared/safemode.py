#-----------------------------------------------------------------------------
# Handle fatal exceptions.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

import time
import board
import storage
import supervisor
import microcontroller

from log_writer import Logger
g_logger = Logger('/sd/safemode.log')

import hw_helper

try:
  import config
  TEST_MODE = config.TEST_MODE
except:
  TEST_MODE = False

# --- configure hardware   ---------------------------------------------------

if not hw_helper.init_sd(config):
  # no way to log anything, just reset
  microcontroller.reset()

try:
  i2c = hw_helper.init_i2c(config)
  the_rtc = hw_helper.init_rtc(config,i2c)
  ts = the_rtc.print_ts(the_rtc.rtc_ext.datetime)
except:
  ts = "???"

reason = (f"{supervisor.runtime.safe_mode_reason}").split(".")[-1]
g_logger.print(f"safemode at {ts} with reason: {reason}")
microcontroller.reset()
