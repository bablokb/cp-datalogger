#-----------------------------------------------------------------------------
# Gateway-task: buffer data to sd-card for later processing
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

import time

from log_writer import Logger
g_logger = Logger()

def _get_buffer_file(config):
  """ query name of buffer-file """
  if config.HAVE_SD:
    return "/sd/tx_buffer.csv"
  try:
    import os
    os.listdir("/saves")
    return "/saves/tx_buffer.csv"
  except:
    return None

def run(config, app, msg_type, values):
  """ buffer data to sd-card """

  buffer_file = _get_buffer_file(config)
  if not buffer_file:
    return

  g_logger.print(f"gateway: buffering data to {buffer_file}...")
  with open(buffer_file, "a") as f:
    f.write(f"{','.join(values)}\n")
