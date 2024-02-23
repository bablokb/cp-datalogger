#-----------------------------------------------------------------------------
# Task: send data using LoRa (adafruit_rfm9x.py)
#
# Authors: Syed Omer Ali, Björn Haßler
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

from log_writer import Logger
g_logger = Logger()

from singleton import singleton

from lora import LORA

def run(config,app):
  """ send data using LoRa """
  lora = LORA(config)
  if lora.transmit(app.record):
    g_logger.print("LoRa: ... successful")
    app.lora_status = 'T'
  else:
    g_logger.print("LoRa: ... failed")
    app.lora_status = 'F'
