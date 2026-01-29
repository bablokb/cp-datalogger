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

def run(config, app, msg_type, values):
  """ buffer data to sd-card """

  if not getattr(config,"HAVE_SD",False):
    return

  csv_file = "/sd/tx_buffer.csv"
  g_logger.print(f"gateway: buffering data to {csv_file}...")
  with open(csv_file, "a") as f:
    f.write(f"{','.join(values)}\n")
