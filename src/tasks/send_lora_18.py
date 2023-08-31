#-----------------------------------------------------------------------------
# Task: send data using LoRa but only once after 18:00
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

from log_writer import Logger
g_logger = Logger()

from . import send_lora

def run(config,app):
  """ send data using LoRa """

  # run only once a day after 18:00 (assuming intervals of at least 5 minutes)
  h = app.data["ts"].tm_hour
  m = app.data["ts"].tm_min

  if h < 18 or h > 18:
    return
  elif m > 5:
    return

  # delegate to unconditional send-method
  send_lora.run(config,app)
