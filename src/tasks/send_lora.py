#-----------------------------------------------------------------------------
# Task: send data using LoRa (adafruit_rfm9x.py)
#
# Authors: Syed Omer Ali, Björn Haßler
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import busio
from log_writer import Logger
g_logger = Logger()

from singleton import singleton
from lora import LORA
import pins

def run(config,app):
  """ send data using LoRa """
  if app.spi and pins.PIN_SD_SCK == pins.PIN_LORA_SCK:
    spi1 = app.spi
  else:
    spi1 = busio.SPI(pins.PIN_LORA_SCK,pins.PIN_LORA_MOSI,
                     pins.PIN_LORA_MISO)

  lora = LORA(config,spi1)
  if lora.transmit(app.record):
    g_logger.print("LoRa: ... successful")
    app.lora_status = 'T'
  else:
    g_logger.print("LoRa: ... failed")
    app.lora_status = 'F'
