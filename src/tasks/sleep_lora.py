#-----------------------------------------------------------------------------
# Task: activate sleep mode for RFM95W chip.
#
# After POR the RFM95W is not in sleep-mode. This tasks saves about 3mA@5V,
# which is especially useful if power-management is not available.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

import os

from log_writer import Logger
g_logger = Logger()

import hw_helper
from lora import LORA
import pins

def run(config,app):
  """ activate sleep-mode for RFM95W """

  try:
    # this will return an existing singleton
    g_logger.print("sleep_lora: fetching LoRa-singleton...")
    lora = LORA(None)
  except:
    g_logger.print("sleep_lora: ... failed.")
    g_logger.print("sleep_lora: creating LoRa-singleton")
    lora = LORA(config)
  lora.sleep()
