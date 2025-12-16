#-----------------------------------------------------------------------------
# Task: send data using LoRa (adafruit_rfm9x.py)
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import busio
from log_writer import Logger
g_logger = Logger()

from lora import LORA
import pins

def run(config,app):
  """ send data using LoRa """

  try:
    # this will return an existing singleton
    g_logger.print("send_lora: fetching LoRa-singleton...")
    lora = LORA(None,None)
  except:
    g_logger.print("send_lora: ... failed.")
    g_logger.print("send_lora: creating LoRa-singleton")
    if app.spi and pins.PIN_SD_SCK == pins.PIN_LORA_SCK:
      spi1 = app.spi
    else:
      spi1 = busio.SPI(pins.PIN_LORA_SCK,pins.PIN_LORA_MOSI,
                       pins.PIN_LORA_MISO)
    lora = LORA(config,spi1)

  rc = lora.send_single(app.record)
  app.lora_status = 'T' if rc else 'F'
