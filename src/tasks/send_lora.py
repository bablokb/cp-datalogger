#-----------------------------------------------------------------------------
# Task: send data using LoRa (adafruit_rfm9x.py)
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import busio
import os

from log_writer import Logger
g_logger = Logger()

from lora import LORA
import pins

def _send_pending(config, lora):
  """ send pending data (failed records from the past)"""

  max_failed = getattr(config,"LORA_MAX_FAILED",5)
  g_logger.print(f"send_lora: processing old (failed) records (max: {max_failed})")
  pending_new = None
  rc_all = True
  i = 0
  with open("/sd/lora_tx_pending.csv","rt") as file:
    for record in file:
      if not rc_all or i >= max_failed:
        # we either already failed or processed enough lines,
        # so move records to pending_new
        lora.trace(f"send_lora: saving old record {i}")
        if not pending_new:
          pending_new = open("/sd/lora_tx_pending_new.csv","at")
        pending_new.write(record)
      else:
        lora.trace(f"send_lora: sending old record {i}")
        rc = lora.send_single(record.strip('\n'))
        rc_all = rc and rc_all
        if not rc:
          if i == 0:
            # failed at the first record, bail out
            return False
          elif not pending_new:
            pending_new = open("/sd/lora_tx_pending_new.csv","at")
          # keep this record in pending_new
          pending_new.write(record)
      i += 1

  # at this stage, lora_tx_pending.csv is processed
  os.remove("/sd/lora_tx_pending.csv")
  if pending_new:
    pending_new.flush()
    pending_new.close()
    os.rename("/sd/lora_tx_pending_new.csv","/sd/lora_tx_pending.csv")
  os.sync()

  # return send-status
  return rc_all

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

  # check for pending records
  if config.HAVE_SD and app.file_exists("/sd/lora_tx_pending.csv"):
    rc = _send_pending(config, lora)
    if not rc:
      # failed again, append current record without even trying
      g_logger.print("send_lora: appending current record to pending-buffer")
      with open("/sd/lora_tx_pending.csv","at") as file:
        file.write(f"{app.record}\n")
      app.lora_status = 'F'
      return

  # try to send current record
  g_logger.print("send_lora: sending current record")
  rc = lora.send_single(app.record)
  app.lora_status = 'T' if rc else 'F'
  if not rc:
    # failed again, append current record
    g_logger.print("send_lora: appending failed record to pending-buffer")
    with open("/sd/lora_tx_pending.csv","at") as file:
      file.write(f"{app.record}\n")
